'use client';

import { useEffect, useState } from 'react';

interface UserStats {
  username: string;
  target_calories: number;
  current_calories: number;
  protein: number;
  fat: number;
  carbs: number;
}

export default function Home() {
  const [stats, setStats] = useState<UserStats>({
    username: 'Атлет',
    target_calories: 2610,
    current_calories: 0,
    protein: 0,
    fat: 0,
    carbs: 0,
  });

  useEffect(() => {
    // Проверяем, что код выполняется в Telegram
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.expand();
      if (tg.setHeaderColor) tg.setHeaderColor('#f6f7fb');

      const user = tg.initDataUnsafe?.user;
      if (user?.id) {
        // Делаем запрос к нашему бэкенду FastAPI
        fetch(`/api/user/${user.id}`)
          .then((res) => res.json())
          .then((data) => setStats(data))
          .catch((err) => console.error('Ошибка загрузки данных:', err));
      }
    }
  }, []);

  const percent = Math.min(100, Math.round((stats.current_calories / stats.target_calories) * 100)) || 0;
  // Вычисляем смещение круга для SVG прогресс-бара (длина окружности 2 * PI * 48 = 301.6)
  const strokeDashoffset = 301.6 - (percent / 100) * 301.6;

  const triggerAction = (type: string) => {
    if ((window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.sendData(JSON.stringify({ type }));
      tg.close();
    }
  };

  return (
    <div style={{ backgroundColor: '#f6f7fb', minHeight: '100vh', color: '#131313', paddingBottom: '90px' }}>
      {/* Шапка */}
      <div style={{ padding: '20px 20px 10px' }}>
        <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 800 }}>
          Привет, {stats.username}! <span style={{ background: '#7f3dff', color: 'white', fontSize: '11px', padding: '2px 6px', borderRadius: '6px' }}>PRO</span>
        </h1>
        <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#8e8e93' }}>Твой трекер активности и питания</p>
      </div>

      {/* Круговой Виджет */}
      <div style={{ background: '#ffffff', margin: '10px 20px', padding: '20px', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '25px', boxShadow: '0 8px 24px rgba(127, 61, 255, 0.06)' }}>
        <div style={{ position: 'relative', width: '110px', height: '110px' }}>
          <svg width="110" height="110">
            <circle cx="55" cy="55" r="48" stroke="#f0eded" strokeWidth="8" fill="transparent" />
            <circle cx="55" cy="55" r="48" stroke="#7f3dff" strokeWidth="8" fill="transparent" 
                    strokeDasharray="301.6" strokeDashoffset={strokeDashoffset} strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.3s ease' }} />
          </svg>
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
            <span style={{ fontSize: '22px', fontWeight: 800, display: 'block' }}>{percent}%</span>
            <span style={{ fontSize: '11px', color: '#8e8e93' }}>от цели</span>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '13px', color: '#8e8e93', fontWeight: 600, marginBottom: '4px' }}>Калории сегодня</div>
          <div style={{ fontSize: '18px', fontWeight: 700, marginBottom: '12px' }}>
            <span>{stats.current_calories}</span> / {stats.target_calories} ккал
          </div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '12px', fontWeight: 600 }}>
            <div style={{ color: '#2ecc71' }}>Белки<span style={{ display: 'block', fontSize: '14px', fontWeight: 700, color: '#131313' }}>{stats.protein}г</span></div>
            <div style={{ color: '#f1c40f' }}>Жиры<span style={{ display: 'block', fontSize: '14px', fontWeight: 700, color: '#131313' }}>{stats.fat}г</span></div>
            <div style={{ color: '#3498db' }}>Углев.<span style={{ display: 'block', fontSize: '14px', fontWeight: 700, color: '#131313' }}>{stats.carbs}г</span></div>
          </div>
        </div>
      </div>

      {/* Баннер AI */}
      <div onClick={() => triggerAction('ask_nutritionist')} style={{ background: 'linear-gradient(135deg, #f3ecff 0%, #f9f6ff 100%)', margin: '20px', padding: '16px', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid rgba(127, 61, 255, 0.12)', cursor: 'pointer' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ background: '#ffffff', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#7f3dff' }}>
            ✨
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 700 }}>Задать вопрос нутрициологу</h3>
            <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#8e8e93' }}>Персональный ответ от AI в Telegram</p>
          </div>
        </div>
      </div>

      {/* Кнопка добавления */}
      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <button onClick={() => triggerAction('add_food_text')} style={{ background: '#7f3dff', color: 'white', border: 'none', padding: '14px 30px', borderRadius: '14px', fontSize: '15px', fontWeight: 700, boxShadow: '0 4px 15px rgba(127, 61, 255, 0.25)', cursor: 'pointer' }}>
          ✨ Добавить еду текстом
        </button>
      </div>
    </div>
  );
}
