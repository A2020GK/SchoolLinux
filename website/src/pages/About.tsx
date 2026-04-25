import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
    faSatellite,
    faGlobe,
    faPlug,
    faGamepad,
    faChalkboardUser,
    faChartLine,
    faLock,
    faDatabase,
    faVial,
    faServer,
    faNetworkWired,
    faGraduationCap,
    faBolt,
    faArrowTrendUp,
    faPeopleGroup,
    faGears,
    faTerminal,
    faRoute,
} from '@fortawesome/free-solid-svg-icons'
import './About.css'

export const About = () => {
    return (
        <div className="about">
            <section className="about-hero">
                <div className="container">
                    <h1>О проекте SchoolLinux</h1>
                    <p className="lead">
                        Инструмент для проведения практических работ по терминалу Linux в школьной среде
                    </p>
                </div>
            </section>

            <section className="section-spacing">
                <div className="container">
                    <h2>Описание проекта</h2>
                    <p>
                        SchoolLinux разработан как учебный тренажёр для информатики в условиях массового перехода
                        российских школ на Linux-дистрибутивы. Цель проекта — сделать изучение терминала не формальным,
                        а практическим и вовлекающим.
                    </p>
                    <p>
                        Учитель управляет занятием централизованно, а ученики подключаются через браузер без установки
                        дополнительного ПО. Это позволяет запускать урок в обычном компьютерном классе с минимальной
                        предварительной настройкой.
                    </p>
                    <p>
                        Важно: SchoolLinux не позиционируется как полноценная LMS. Это специализированный практикум,
                        который закрывает именно сценарий проведения терминальных лабораторных работ.
                    </p>
                </div>
            </section>

            <section className="section-spacing">
                <div className="container">
                    <h2>Почему не только готовые аналоги</h2>
                    <p>
                        Тренажёры типа OverTheWire (Bandit) полезны для самостоятельной практики,
                        но слабо интегрируются в школьный урок:
                        у преподавателя нет централизованного управления классом, гибкой настройки сценария,
                        сквозного мониторинга и автоматического экспорта результатов группы.
                    </p>
                </div>
            </section>

            <section className="tech-stack section-spacing">
                <div className="container">
                    <h2>Технический стек</h2>
                    <div className="tech-grid">
                        <div className="tech-card">
                            <h3>Бэкенд</h3>
                            <ul>
                                <li><strong>Python 3.12</strong> и <strong>FastAPI</strong></li>
                                <li><strong>Pydantic</strong> для валидации состояния</li>
                                <li><strong>Paramiko</strong> для SSH-развёртывания</li>
                                <li><strong>Socket.IO</strong> для real-time событий</li>
                                <li><strong>pytest</strong> и CI для стабильности</li>
                            </ul>
                        </div>
                        <div className="tech-card">
                            <h3>Фронтенд</h3>
                            <ul>
                                <li><strong>React + TypeScript</strong></li>
                                <li><strong>Vite</strong> для сборки</li>
                                <li><strong>Axios</strong> для API</li>
                                <li>Отдельные интерфейсы ученика и учителя</li>
                            </ul>
                        </div>
                        <div className="tech-card">
                            <h3>Состояние и процессы</h3>
                            <ul>
                                <li>Типизированный <strong>JSON state</strong></li>
                                <li>Восстановление после перезапуска</li>
                                <li>Сценарии: установка, проверка, очистка</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <section className="section-spacing">
                <div className="container">
                    <h2>Архитектура системы</h2>
                    <div className="architecture-list">
                        <div className="arch-item">
                            <h3><FontAwesomeIcon icon={faSatellite} /> Сервер на машине учителя</h3>
                            <p>
                                Серверная часть выполняет развёртывание заданий, проверку ответов, подсчёт баллов
                                и управление раундом.
                            </p>
                        </div>
                        <div className="arch-item">
                            <h3><FontAwesomeIcon icon={faGlobe} /> Веб-клиент без установки</h3>
                            <p>
                                Ученики работают в браузере, регистрируются по имени, а идентификация и маршрутизация
                                событий выполняются по IP-адресу подключения.
                            </p>
                        </div>
                        <div className="arch-item">
                            <h3><FontAwesomeIcon icon={faPlug} /> Плагинные сценарии</h3>
                            <p>
                                Каждый режим игры изолирован в отдельном модуле с методами инициализации, проверки
                                и очистки, поэтому новые сценарии можно добавлять без изменения ядра.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="features-detailed section-spacing">
                <div className="container">
                    <h2>Ключевые функции</h2>
                    <div className="features-list">
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faGamepad} /> Два режима обучения</h3>
                            <p>
                                Режим поиска: ученик ищет строки с префиксом <strong>klad:</strong> в индивидуальном
                                файловом дереве с настраиваемой сложностью.
                            </p>
                            <p>
                                Режим создания: ученик строит структуру каталогов и файлов по условиям преподавателя,
                                после чего получает автоматическую проверку.
                            </p>
                        </div>
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faChalkboardUser} /> Панель преподавателя</h3>
                            <p>
                                Выбор сценария, параметры сложности, запуск и остановка раунда, контроль статусов,
                                экспорт итоговой таблицы в CSV.
                            </p>
                        </div>
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faChartLine} /> События в реальном времени</h3>
                            <p>
                                Socket.IO мгновенно синхронизирует изменения в интерфейсах: список учеников,
                                состояние раунда, результаты проверки.
                            </p>
                        </div>
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faLock} /> SSH-развёртывание и очистка</h3>
                            <p>
                                Перед раундом система разворачивает среду на ученических машинах, а после завершения
                                автоматически удаляет созданные файлы и возвращает окружение в исходное состояние.
                            </p>
                        </div>
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faDatabase} /> Прозрачное состояние</h3>
                            <p>
                                Состояние хранится в JSON и восстанавливается после перезапуска сервера,
                                что позволяет проводить несколько раундов без повторной регистрации.
                            </p>
                        </div>
                        <div className="feature-item">
                            <h3><FontAwesomeIcon icon={faVial} /> Проверенное качество</h3>
                            <p>
                                Серверная логика покрыта тестами, а CI-пайплайн автоматически проверяет изменения
                                при обновлении кода.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="requirements section-spacing">
                <div className="container">
                    <h2>Минимальные требования</h2>
                    <div className="requirements-grid">
                        <div className="req-card">
                            <h3><FontAwesomeIcon icon={faServer} /> Учительская машина</h3>
                            <ul>
                                <li>Linux, Python 3.12+, Node.js 18+</li>
                                <li>Доступ к сети класса</li>
                                <li>Запуск сервера на порту 8000</li>
                            </ul>
                        </div>
                        <div className="req-card">
                            <h3><FontAwesomeIcon icon={faNetworkWired} /> Ученические машины</h3>
                            <ul>
                                <li>Linux и SSH на порту 22</li>
                                <li>Единые SSH-учётные данные</li>
                                <li>Доступ к интерфейсу через браузер</li>
                            </ul>
                        </div>
                        <div className="req-card">
                            <h3><FontAwesomeIcon icon={faRoute} /> Сеть</h3>
                            <ul>
                                <li>Стабильная локальная сеть класса</li>
                                <li>Порт 8000 для backend, 4000 для dev-frontend</li>
                                <li>Для production рекомендуется reverse proxy</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <section className="installation section-spacing">
                <div className="container">
                    <h2>Быстрый запуск</h2>
                    <div className="install-steps">
                        <div className="step">
                            <h3><FontAwesomeIcon icon={faGlobe} /> Клонирование</h3>
                            <code>git clone https://github.com/A2020GK/SchoolLinux</code>
                        </div>
                        <div className="step">
                            <h3><FontAwesomeIcon icon={faTerminal} /> Зависимости Python</h3>
                            <code>pip install -r requirements.txt</code>
                        </div>
                        <div className="step">
                            <h3><FontAwesomeIcon icon={faGears} /> Переменные окружения</h3>
                            <p>Укажите <code>SSH_USER</code> и <code>SSH_PASSWORD</code> в файле <code>.env</code>.</p>
                        </div>
                        <div className="step">
                            <h3><FontAwesomeIcon icon={faServer} /> Запуск backend</h3>
                            <code>fastapi run --host 0.0.0.0</code>
                        </div>
                        <div className="step">
                            <h3><FontAwesomeIcon icon={faGlobe} /> Запуск frontend</h3>
                            <code>npx vite --host 0.0.0.0 --port 4000</code>
                        </div>
                    </div>
                </div>
            </section>

            <section className="results section-spacing">
                <div className="container">
                    <h2>Результаты апробации</h2>
                    <div className="results-grid">
                        <div className="result-card">
                            <h3><FontAwesomeIcon icon={faGraduationCap} /> Тестирование в школе</h3>
                            <p>
                                Апробация проведена в Школе №192 на уроках информатики в 9В и 10В классах
                                на дистрибутиве МОС 12.
                            </p>
                        </div>
                        <div className="result-card">
                            <h3><FontAwesomeIcon icon={faBolt} /> Производительность</h3>
                            <p>
                                Система стабильно работала при одновременном развёртывании среды на 25-30 машинах.
                            </p>
                        </div>
                        <div className="result-card">
                            <h3><FontAwesomeIcon icon={faArrowTrendUp} /> Эффективность обучения</h3>
                            <p>
                                По итогам апробации ученики, применявшие grep и find, завершали поиск в среднем
                                на 30-40% быстрее.
                            </p>
                        </div>
                        <div className="result-card">
                            <h3><FontAwesomeIcon icon={faPeopleGroup} /> Обратная связь</h3>
                            <p>
                                Получены положительные отзывы: отмечены удобство мониторинга и высокая скорость
                                запуска занятия.
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
