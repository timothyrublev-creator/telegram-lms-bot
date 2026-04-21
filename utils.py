from openpyxl import Workbook
from database import get_db
import io

def export_masters_to_excel():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, name, rating_points, game_score, balance, subscription_end 
        FROM users WHERE role = 'student'
    """)
    users = cursor.fetchall()
    conn.close()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Мастера"
    ws.append(["ID", "Имя", "Рейтинг", "Очки игры", "Баланс", "Подписка до"])
    
    for u in users:
        ws.append([u['user_id'], u['name'], u['rating_points'], u['game_score'], u['balance'], u['subscription_end']])
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer