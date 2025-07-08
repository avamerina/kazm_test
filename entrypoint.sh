#!/bin/bash
set -e

echo "🔍 Проверяем состояние базы данных..."

# Функция для ожидания готовности базы данных
wait_for_db() {
    echo "⏳ Ожидаем готовности базы данных..."
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\q' 2>/dev/null; do
        echo "База данных еще не готова, ждем..."
        sleep 2
    done
    echo "✅ База данных готова"
}

# Ждем готовности базы данных
wait_for_db

# Проверяем, существует ли схема content и таблицы
SCHEMA_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'content';")

# Проверяем, есть ли данные в таблицах
if [ "$SCHEMA_EXISTS" = "content" ]; then
    # Проверяем количество записей в основных таблицах
    FILM_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.film_work;" 2>/dev/null || echo "0")
    GENRE_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.genre;" 2>/dev/null || echo "0")
    PERSON_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.person;" 2>/dev/null || echo "0")
    
    TOTAL_RECORDS=$((FILM_COUNT + GENRE_COUNT + PERSON_COUNT))
    
    if [ "$TOTAL_RECORDS" -gt 0 ]; then
        echo "🔄 База данных уже содержит данные. Пропускаем инициализацию."
        FIRST_RUN=false
    else
        echo "📊 Схема существует, но данных нет. Применяем init.sql..."
        FIRST_RUN=true
    fi
else
    echo "🆕 Первый запуск: схема content не существует. Применяем миграции и init.sql..."
    FIRST_RUN=true
fi

if [ "$FIRST_RUN" = true ]; then
    echo "🚀 Применяем Alembic миграции..."
    alembic upgrade head
    
    # Применяем init.sql, если он существует
    if [ -f /app/init.sql ]; then
        echo "📥 Применяем init.sql..."
        PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -f /app/init.sql
        
        # Проверяем, что данные были загружены
        FILM_COUNT_AFTER=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.film_work;" 2>/dev/null || echo "0")
        GENRE_COUNT_AFTER=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.genre;" 2>/dev/null || echo "0")
        PERSON_COUNT_AFTER=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT COUNT(*) FROM content.person;" 2>/dev/null || echo "0")
        
        echo "✅ Инициализация завершена:"
        echo "   - Фильмы: $FILM_COUNT_AFTER"
        echo "   - Жанры: $GENRE_COUNT_AFTER"
        echo "   - Персоны: $PERSON_COUNT_AFTER"
    else
        echo "⚠️  Файл init.sql не найден"
    fi
else
    echo "✅ База данных уже инициализирована, пропускаем миграции и дамп"
fi

# Запускаем приложение
echo "▶ Запуск uvicorn..."
exec uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8000
