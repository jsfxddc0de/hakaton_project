import React, { useState } from 'react';
import { profileData } from '../../data/mockData';

function Profile() {
  const [formData, setFormData] = useState(profileData);

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Данные сохранены!');
    console.log('Form data:', formData);
  };

  return (
    <div className="profile-container page-profile">
      <div className="profile-header">
        <h1 className="profile-title">Заполнение профиля</h1>
        <p className="profile-subtitle">Пожалуйста, укажите актуальные данные для участия в бале</p>
      </div>

      <form className="profile-form" onSubmit={handleSubmit}>
        <div className="profile-top-block">
          <div className="avatar-placeholder">+ Фото</div>
          <div className="fio-input-wrapper">
            <div className="input-group">
              <label htmlFor="fullName">Ваше полное ФИО</label>
              <input
                type="text"
                id="fullName"
                className="form-input"
                placeholder="Например: Иванов Иван Иванович"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
            </div>
          </div>
        </div>

        <div className="input-grid">
          <div className="input-group">
            <label htmlFor="class">Класс / Группа</label>
            <input
              type="text"
              id="class"
              className="form-input"
              placeholder="Введите ваш класс или группу"
              value={formData.class}
              onChange={handleChange}
            />
          </div>
          <div className="input-group">
            <label htmlFor="email">Электронная почта (Email)</label>
            <input
              type="email"
              id="email"
              className="form-input"
              placeholder="example@mail.ru"
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          <div className="input-group">
            <label htmlFor="gender">Пол</label>
            <input
              type="text"
              id="gender"
              className="form-input"
              placeholder="Мужской / Женский"
              value={formData.gender}
              onChange={handleChange}
            />
          </div>
          <div className="input-group">
            <label htmlFor="city">Город</label>
            <input
              type="text"
              id="city"
              className="form-input"
              placeholder="Укажите ваш город"
              value={formData.city}
              onChange={handleChange}
            />
          </div>
        </div>

        <button type="submit" className="btn-submit">Сохранить изменения</button>
      </form>
    </div>
  );
}

export default Profile;