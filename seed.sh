#!/bin/sh
# Müəllim üçün: bazanı sıfırla və dərsin SONUNDAKI tam məlumatı yüklə (tək komanda).
#   ./seed.sh
# Nəticə: db.sqlite3 yenidən yaranır, bütün migration-lar tətbiq olunur,
#         blog/fixtures/demo_full.json yüklənir (admin / step12345 superuser daxildir).
# Növbəti dərsə bu qovluğun surəti üzərindən başlayanda da eyni komanda işləyir.
set -e
cd "$(dirname "$0")"
rm -f db.sqlite3
uv run manage.py migrate -v 0
uv run manage.py loaddata demo_full
echo "✔ Baza hazırdır.  Admin: admin / step12345   (digər user-lər: parol step12345)"
echo "  uv run manage.py runserver  →  http://127.0.0.1:8000/admin/"
