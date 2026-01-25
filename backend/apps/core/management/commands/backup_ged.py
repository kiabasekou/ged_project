"""
Management command pour backup automatisé de la GED.
Usage: python manage.py backup_ged
"""
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cryptography.fernet import Fernet


class Command(BaseCommand):
    help = 'Crée un backup chiffré complet de la base de données et des fichiers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='/backups',
            help='Répertoire de destination des backups'
        )
        parser.add_argument(
            '--encrypt',
            action='store_true',
            default=True,
            help='Chiffrer le backup (activé par défaut)'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            default=True,
            help='Inclure les fichiers media (activé par défaut)'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.stdout.write(self.style.SUCCESS(
            f"[{timestamp}] Démarrage du backup..."
        ))
        
        # Créer le répertoire de backup
        output_dir.mkdir(parents=True, exist_ok=True)
        backup_name = f"ged_backup_{timestamp}"
        backup_path = output_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        try:
            # 1. Backup de la base de données PostgreSQL
            self.stdout.write("📦 Backup de la base de données...")
            db_backup_file = self._backup_database(backup_path, timestamp)
            
            # 2. Backup des fichiers media (si demandé)
            media_backup_file = None
            if options['include_media']:
                self.stdout.write("📁 Backup des fichiers media...")
                media_backup_file = self._backup_media(backup_path, timestamp)
            
            # 3. Chiffrement des backups (si demandé)
            if options['encrypt']:
                self.stdout.write("🔐 Chiffrement des backups...")
                encrypted_files = self._encrypt_backups(
                    backup_path,
                    [db_backup_file, media_backup_file]
                )
            
            # 4. Compression finale
            self.stdout.write("🗜️  Compression du backup...")
            archive_file = self._create_archive(backup_path, output_dir, backup_name)
            
            # 5. Nettoyage des fichiers temporaires
            shutil.rmtree(backup_path)
            
            # 6. Rotation des anciens backups
            self._rotate_old_backups(output_dir)
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Backup terminé avec succès!"
                f"\n📍 Emplacement: {archive_file}"
                f"\n📊 Taille: {self._get_file_size(archive_file)}"
            ))
            
        except Exception as e:
            raise CommandError(f"Échec du backup: {str(e)}")

    def _backup_database(self, backup_path: Path, timestamp: str) -> Path:
        """Dump PostgreSQL"""
        db_config = settings.DATABASES['default']
        
        db_backup_file = backup_path / f"database_{timestamp}.sql"
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        cmd = [
            'pg_dump',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-F', 'c',  # Format custom (compressé)
            '-f', str(db_backup_file),
            '--verbose'
        ]
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Base de données sauvegardée: {self._get_file_size(db_backup_file)}"
            ))
            return db_backup_file
        except subprocess.CalledProcessError as e:
            raise CommandError(f"Échec pg_dump: {e.stderr.decode()}")

    def _backup_media(self, backup_path: Path, timestamp: str) -> Path:
        """Archive tar.gz des fichiers media"""
        media_root = Path(settings.MEDIA_ROOT)
        media_backup_file = backup_path / f"media_{timestamp}.tar.gz"
        
        if not media_root.exists():
            self.stdout.write(self.style.WARNING("  ⚠ Aucun fichier media à sauvegarder"))
            return None
        
        try:
            shutil.make_archive(
                str(media_backup_file.with_suffix('')),
                'gztar',
                media_root
            )
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Fichiers media sauvegardés: {self._get_file_size(media_backup_file)}"
            ))
            return media_backup_file
        except Exception as e:
            raise CommandError(f"Échec backup media: {str(e)}")

    def _encrypt_backups(self, backup_path: Path, files: list) -> list:
        """Chiffrement AES-256 via Fernet"""
        encryption_key = getattr(settings, 'BACKUP_ENCRYPTION_KEY', None)
        
        if not encryption_key:
            self.stdout.write(self.style.WARNING(
                "  ⚠ BACKUP_ENCRYPTION_KEY manquante, backup non chiffré"
            ))
            return files
        
        cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        encrypted_files = []
        
        for file_path in files:
            if not file_path or not file_path.exists():
                continue
            
            encrypted_file = file_path.with_suffix(file_path.suffix + '.enc')
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = cipher.encrypt(data)
            
            with open(encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Supprimer le fichier non chiffré
            file_path.unlink()
            
            encrypted_files.append(encrypted_file)
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Fichier chiffré: {encrypted_file.name}"
            ))
        
        return encrypted_files

    def _create_archive(self, backup_path: Path, output_dir: Path, backup_name: str) -> Path:
        """Compression finale en tar.gz"""
        archive_file = output_dir / f"{backup_name}.tar.gz"
        
        shutil.make_archive(
            str(archive_file.with_suffix('')),
            'gztar',
            backup_path.parent,
            backup_path.name
        )
        
        return archive_file

    def _rotate_old_backups(self, output_dir: Path, retention_days: int = 30):
        """Suppression des backups de plus de N jours"""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        for backup_file in output_dir.glob("ged_backup_*.tar.gz"):
            # Extraction de la date du nom de fichier
            try:
                date_str = backup_file.stem.split('_')[-2] + backup_file.stem.split('_')[-1]
                backup_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                backup_date = timezone.make_aware(backup_date)
                
                if backup_date < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            except (ValueError, IndexError):
                continue
        
        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {deleted_count} ancien(s) backup(s) supprimé(s)"
            ))

    def _get_file_size(self, file_path: Path) -> str:
        """Formatage taille fichier"""
        if not file_path.exists():
            return "0 o"
        
        size = file_path.stat().st_size
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} To"
