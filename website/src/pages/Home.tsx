import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faGithub, faLinux } from '@fortawesome/free-brands-svg-icons'
import {
    faTerminal,
    faUsers,
    faGlobe,
    faChartLine,
    faMagnifyingGlass,
    faFolderTree,
    faArrowRight,
    faDisplay,
    faBook,
} from '@fortawesome/free-solid-svg-icons'
import { FeatureCard } from '../components/FeatureCard'
import './Home.css'

export const Home = () => {
    const presentationPdfUrl = `${import.meta.env.BASE_URL}SchoolLinux 3 - Презентация.pdf`
    const fullDescriptionPdfUrl = `${import.meta.env.BASE_URL}SchoolLinux 3 - Полное описание.pdf`

    return (
        <div className="home" id="top">
            <section className="hero section-spacing">
                <div className="container">
                    <div className="hero-content">
                        <h1><FontAwesomeIcon icon={faLinux} /> SchoolLinux</h1>
                        <p className="hero-subtitle">
                            Инструмент для проведения практических работ по терминалу Linux на уроках информатики
                        </p>
                    </div>
                </div>
            </section>

            <section className="problem-solution section-spacing" id="problem">
                <div className="container">
                    <div className="ps-grid">
                        <div className="ps-card">
                            <h3>Проблема</h3>
                            <p>
                                В условиях перехода школ на российские Linux-дистрибутивы (МОС, ALT Linux,
                                Astra Linux и другие) ученикам нужны практические навыки командной строки.
                                При этом традиционное изучение терминала часто остаётся формальным и мало вовлекает.
                            </p>
                        </div>
                        <div className="ps-card">
                            <h3>Решение</h3>
                            <p>
                                SchoolLinux позволяет проводить практические работы по использованию терминала Linux на уроках информатики, превращая обучение в интерактивный процесс через игровые механики, 
                                 и мгновенную обратную связь. 
                            </p>
                        </div>
                        <div className="ps-card">
                            <h3>Фокус продукта</h3>
                            <p>
                                SchoolLinux не заменяет полноценную LMS. Это узкоспециализированный инструмент
                                для проведения практических работ по терминалу Linux на уроке информатики, в будущем планируется добавление встроенного курса по Linux для учителей
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="features section-spacing" id="features">
                <div className="container">
                    <h2 className="text-center">Ключевые возможности</h2>
                    <p className="text-center" style={{ marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
                       SchoolLinux предоставляет учителю мощный набор инструментов для создания интерактивных практических работ по терминалу Linux, которые вовлекают учеников в процесс обучения и позволяют эффективно контролировать их прогресс.
                    </p>
                    <div className="grid">
                        <FeatureCard
                            icon={faTerminal}
                            title="Практикум по терминалу"
                            description="Ученики отрабатывают реальные команды Linux в реальной файловой среде, решая поставленные задачи"
                        />
                        <FeatureCard
                            icon={faUsers}
                            title="Централизованное управление"
                            description="Учитель полностью контролирует занятие: выбирает сценарии, настраивает сложность и отслеживает прогресс в реальном времени"
                        />
                        <FeatureCard
                            icon={faGlobe}
                            title="Без установки ПО на компьютерах учеников"
                            description="Ученики взаимодействуют с системой через браузер, вся логика и управление остаются на компьютере учителя. Для запуска нужны только локальная сеть и интерпретатор Python"
                        />
                        <FeatureCard
                            icon={faChartLine}
                            title="Мониторинг и статистика"
                            description="Статусы и результаты обновляются мгновенно во время практической работы, доступен экспорт результатов в формате CSV для дальнейшего анализа и оценки успеваемости учеников"
                        />
                    </div>
                </div>
            </section>

            <section className="section-spacing" id="modes">
                <div className="container">
                    <h2 className="text-center">2 встроенных игровых режима</h2>
                    <div className="grid">
                        <FeatureCard
                            icon={faFolderTree}
                            title="Создание структуры"
                            description="Ученики создают файловое дерево в соответствии с заданием, пряча там «клады», после чего система автоматически проверяет результат."
                        />
                        <FeatureCard
                            icon={faMagnifyingGlass}
                            title="Поиск информации"
                            description={`Ученики находят «клады» (строки вида "klad:...") в сгенерированной файловой структуре с помощью команд терминала.`}
                        />
                    </div>
                  <p className="text-center" style={{ marginTop: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
                        Доступна возможность подключения своих заданий, инструкция есть в README на GitHub.
                    </p>
                </div>
            </section>

            <section className="links-section section-spacing" id="links">
                <div className="container">
                    <h2 className="text-center">Ресурсы проекта</h2>
                    <div className="links-grid">
                        <a href={presentationPdfUrl} target="_blank" rel="noopener noreferrer" className="link-card card">
                            <h3><FontAwesomeIcon icon={faDisplay} /> Презентация</h3>
                            <p>Презентация проекта, подготовленная для конференции "Инженеры будущего" (PDF)</p>
                            <span className="link-arrow">
                                <FontAwesomeIcon icon={faArrowRight} />
                            </span>
                        </a>
                        <a href={fullDescriptionPdfUrl} target="_blank" rel="noopener noreferrer" className="link-card card">
                            <h3><FontAwesomeIcon icon={faBook} /> Полное описание проекта</h3>
                            <p>Подробное описание функционала и использования SchoolLinux (PDF)</p>
                            <span className="link-arrow">
                                <FontAwesomeIcon icon={faArrowRight} />
                            </span>
                        </a>
                        <a href="https://github.com/A2020GK/SchoolLinux#2-руководство-по-установке" target="_blank" rel="noopener noreferrer" className="link-card card">
                            <h3><FontAwesomeIcon icon={faMagnifyingGlass} /> Руководство по запуску</h3>
                            <p>Быстрая инструкция по установке и запуску инструмента в компьютерном классе (GitHub)</p>
                            <span className="link-arrow">
                                <FontAwesomeIcon icon={faArrowRight} />
                            </span>
                        </a>
                        <a href="https://forms.yandex.ru/u/69ee1aefe010db68d20ccb82" target="_blank" rel="noopener noreferrer" className="link-card card">
                            <h3><FontAwesomeIcon icon={faUsers} /> Обратная связь</h3>
                            <p>Оставить отзыв и предложения по развитию SchoolLinux (Яндекс.Формы)</p>
                            <span className="link-arrow">
                                <FontAwesomeIcon icon={faArrowRight} />
                            </span>
                        </a>
                    </div>
                </div>
            </section>

            <section className="cta section-spacing" id="github">
                <div className="container">
                    <div className="cta-content text-center">
                        <h2><FontAwesomeIcon icon={faFolderTree} /> GitHub</h2>
                        <p style={{ marginBottom: '2rem' }}>
                            Исходный код проекта, инструкции по запуску и руководство по созданию своих заданий доступны в открытом доступе на GitHub.
                        </p>
                        <a href="https://github.com/A2020GK/SchoolLinux" target="_blank" rel="noopener noreferrer" className="button">
                            <FontAwesomeIcon icon={faGithub} /> Открыть репозиторий
                        </a>
                    </div>
                </div>
            </section>
        </div>
    )
}
