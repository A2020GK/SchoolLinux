import { useMemo, useState } from "react";
import { useUsers } from "../contexts/UsersContext";
import { useExtendedGame } from "../contexts/ExtendedGameContext";
import { useGame } from "../contexts/GameContext";
import { setUserKicked } from "../api/user";
import { startGame, stopGame } from "../api/game";
import { DataGrid, type Column, type SortColumn } from "react-data-grid";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faGraduationCap,
    faComputer,
    faUser,
    faGem,
    faPersonCircleMinus,
    faPersonCircleCheck,
    faCircleNodes,
    faCaretRight,
    faPlay,
    faStop,
} from "@fortawesome/free-solid-svg-icons";
import type { GameSettingsItem } from "../types/game";
import {
    notifyError,
    notifySuccess,
    notifyWarning,
} from "../helpers/notify";
import "react-data-grid/lib/styles.css";
import "../styles/teacher.css";

const escapeCsvField = (value: string | number | boolean): string => {
    const text = String(value).replace(/"/g, '""');
    return `"${text}"`;
};

const formatDateForFilename = (date: Date): string => {
    const pad = (value: number) => String(value).padStart(2, "0");
    return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}-${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
};

const slugifyGameType = (raw: string | undefined): string => {
    if (!raw) {
        return "unknown";
    }

    const slug = raw
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");

    return slug || "unknown";
};

interface StudentRow {
    ip: string;
    pcName: string;
    name: string;
    score: number;
    kicked: boolean;
}

const ActionFormatter = ({ row, onKick, onRestore }: {
    row: StudentRow
    onKick: (ip: string) => void
    onRestore: (ip: string) => void
}) => (
    row.kicked ? (
        <button
            className="restore-btn"
            onClick={() => onRestore(row.ip)}
            title="Восстановить ученика"
        >
            <FontAwesomeIcon icon={faPersonCircleCheck} /> Восстановить
        </button>
    ) : (
        <button
            className="kick-btn"
            onClick={() => onKick(row.ip)}
            title="Изгнать ученика"
        >
            <FontAwesomeIcon icon={faPersonCircleMinus} /> Изгнать
        </button>
    )
);

const SettingsInput = ({ 
    setting, 
    onChange,
    disabled
}: { 
    setting: GameSettingsItem
    onChange: (value: string | number | boolean) => void
    disabled: boolean
}) => {
    const currentValue = setting.value ?? setting.default;
    
    switch (setting.type) {
        case "boolean":
            return (
                <input
                    type="checkbox"
                    checked={currentValue === true || currentValue === "true"}
                    onChange={(e) => onChange(e.target.checked)}
                    disabled={disabled}
                    className="setting-checkbox"
                />
            );
        case "number":
            return (
                <input
                    type="number"
                    value={String(currentValue)}
                    onChange={(e) => onChange(parseInt(e.target.value) || 0)}
                    disabled={disabled}
                    className="setting-input"
                />
            );
        case "option":
            return (
                <select
                    value={String(currentValue)}
                    onChange={(e) => onChange(e.target.value)}
                    disabled={disabled}
                    className="setting-select"
                >
                    {setting.options && Object.entries(setting.options).map(([key, label]) => (
                        <option key={key} value={key}>{label}</option>
                    ))}
                </select>
            );
        case "string":
        default:
            return (
                <input
                    type="text"
                    value={String(currentValue)}
                    onChange={(e) => onChange(e.target.value)}
                    disabled={disabled}
                    className="setting-input"
                />
            );
    }
};

export const Teacher = () => {
    const { users, loading: usersLoading, updateUserKicked } = useUsers();
    const { currentGame, gamesList, loading: gamesLoading, setCurrentGame } = useExtendedGame();
    const { gameState } = useGame();
    const [sortColumns, setSortColumns] = useState<readonly SortColumn[]>([]);
    const [startStopLoading, setStartStopLoading] = useState(false);
    const [settingsChanges, setSettingsChanges] = useState<Record<string, string | number | boolean>>({});

    const currentGameKey = currentGame
        ? Object.keys(gamesList || {}).find((key) => gamesList?.[key]?.name === currentGame.name) || undefined
        : undefined;

    const rows: StudentRow[] = useMemo(() => {
        if (!users) return [];
        return Object.entries(users).map(([ip, user]) => ({
            ip,
            pcName: user.pcName,
            name: user.name,
            score: user.score,
            kicked: user.kicked,
        }));
    }, [users]);

    const sortedRows: readonly StudentRow[] = useMemo(() => {
        if (sortColumns.length === 0) return rows;

        return [...rows].sort((a, b) => {
            for (const sort of sortColumns) {
                const aVal = (a as any)[sort.columnKey];
                const bVal = (b as any)[sort.columnKey];

                let compResult = 0;
                if (typeof aVal === "string") {
                    compResult = aVal.localeCompare(bVal);
                } else {
                    compResult = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
                }

                if (compResult !== 0) {
                    return sort.direction === "ASC" ? compResult : -compResult;
                }
            }
            return 0;
        });
    }, [rows, sortColumns]);

    const handleKick = async (ip: string) => {
        // Optimistic update: update local state immediately
        updateUserKicked(ip, true);
        try {
            await setUserKicked(ip, true);
        } catch (error) {
            // Revert on error
            updateUserKicked(ip, false);
            notifyError("Ошибка при изгнании");
            console.error(error);
        }
    };

    const handleRestore = async (ip: string) => {
        // Optimistic update: update local state immediately
        updateUserKicked(ip, false);
        try {
            await setUserKicked(ip, false);
        } catch (error) {
            // Revert on error
            updateUserKicked(ip, true);
            notifyError("Ошибка при восстановлении");
            console.error(error);
        }
    };

    const handleGameChange = async (gameKey: string) => {
        try {
            // Clear settings changes when switching games
            setSettingsChanges({});
            await setCurrentGame(gameKey, undefined);
        } catch (error) {
            if ((error as any).response?.status === 409) {
                notifyWarning("Нельзя менять игру во время выполнения. Сначала остановите игру.");
            } else {
                notifyError("Ошибка при смене игры");
            }
            console.error(error);
        }
    };

    const handleSettingChange = (key: string, value: string | number | boolean) => {
        setSettingsChanges(prev => ({ ...prev, [key]: value }));
    };

    const handleApplySettings = async () => {
        if (!currentGame) return;
        
        try {
            const gameKey = Object.keys(gamesList || {}).find(
                (key) => gamesList?.[key]?.name === currentGame.name
            );
            if (!gameKey) return;

            await setCurrentGame(gameKey, settingsChanges);
            setSettingsChanges({});
            notifySuccess("Параметры применены");
        } catch (error) {
            if ((error as any).response?.status === 409) {
                notifyWarning("Нельзя менять параметры во время выполнения. Сначала остановите игру.");
            } else {
                notifyError("Ошибка при применении параметров");
            }
            console.error(error);
        }
    };

    const handleStartGame = async () => {
        try {
            setStartStopLoading(true);
            await startGame();
        } catch (error) {
            if ((error as any).response?.status === 409) {
                notifyWarning("Не можно начать игру. Сначала остановите предыдущую игру.");
            } else {
                notifyError("Ошибка при запуске игры");
            }
            console.error(error);
        } finally {
            setStartStopLoading(false);
        }
    };

    const handleStopGame = async () => {
        try {
            setStartStopLoading(true);
            await stopGame();
            handleDownloadCsv();
        } catch (error) {
            if ((error as any).response?.status === 409) {
                notifyWarning("Не можно остановить неработающую игру.");
            } else {
                notifyError("Ошибка при остановке игры");
            }
            console.error(error);
        } finally {
            setStartStopLoading(false);
        }
    };

    const handleDownloadCsv = () => {
        if (sortedRows.length === 0) {
            notifyWarning("Нет данных для экспорта");
            return;
        }

        const header = ["IP", "Компьютер", "Имя", "Очки", "Изгнан"];
        const lines = [
            header.join(","),
            ...sortedRows.map((row) => [
                escapeCsvField(row.ip),
                escapeCsvField(row.pcName),
                escapeCsvField(row.name),
                escapeCsvField(row.score),
                escapeCsvField(row.kicked ? "Да" : "Нет"),
            ].join(",")),
        ];

        if (currentGame) {
            lines.push("");
            lines.push(escapeCsvField(`Максимум очков: ${currentGame.requiredUserScore}`));
        }

        const csvContent = lines.join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const fileName = `SL3-${slugifyGameType(currentGameKey || currentGame?.name)}-${formatDateForFilename(new Date())}.csv`;

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        notifySuccess("Таблица результатов скачана");
    };

    const columns: readonly Column<StudentRow>[] = [
        {
            key: "ip",
            name: <><FontAwesomeIcon icon={faCircleNodes} /> IP</>,
            minWidth: 120,
        },
        {
            key: "pcName",
            name: <><FontAwesomeIcon icon={faComputer} /> Компьютер</>,
            sortable: true,
            minWidth: 150,
        },
        {
            key: "name",
            name: <><FontAwesomeIcon icon={faUser} /> Имя</>,
            sortable: true,
            minWidth: 200,
        },
        {
            key: "score",
            name: <><FontAwesomeIcon icon={faGem} /> Очки</>,
            sortable: true,
            minWidth: 80,
        },
        {
            key: "action",
            name: <><FontAwesomeIcon icon={faCaretRight} /> Действие</>,
            minWidth: 130,
            cellClass: "action-cell",
            renderCell: (props) => (
                <ActionFormatter 
                    row={props.row as StudentRow}
                    onKick={handleKick}
                    onRestore={handleRestore}
                />
            ),
            resizable: true,
        },
    ];

    if (usersLoading || gamesLoading) {
        return (
            <main className="teacher-view">
                <p>Загрузка...</p>
            </main>
        );
    }

    return (
        <main className="teacher-view">
            <div className="content">
                <h1>
                    <FontAwesomeIcon icon={faGraduationCap} /> Ученики
                </h1>

                <div className="table-wrapper">
                    <DataGrid
                        columns={columns}
                        rows={sortedRows}
                        sortColumns={sortColumns}
                        onSortColumnsChange={setSortColumns}
                        className="teacher-datagrid"
                    />
                </div>

                {currentGame && (
                    <p className="required-score-footer">Требуемый счёт {currentGame.requiredUserScore}</p>
                )}

                <div className="table-actions">
                    <button className="export-btn" onClick={handleDownloadCsv}>
                        Экспорт CSV
                    </button>
                </div>

                <div className="controls-section">
                    <div className="game-selector">
                        <label htmlFor="game-select">Текущая игра:</label>
                        <select
                            id="game-select"
                            value={currentGameKey || ""}
                            onChange={(e) => e.target.value && handleGameChange(e.target.value)}
                            disabled={gameState === "running"}
                            className={gameState === "running" ? "disabled" : ""}
                        >
                            <option value="">Выберите игру...</option>
                            {gamesList && Object.entries(gamesList).map(([key, game]) => (
                                <option key={key} value={key}>
                                    {game.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {currentGame && (
                        <div className="current-game-info">
                            <h3>{currentGame.name}</h3>
                            <p>{currentGame.description}</p>

                            {/* Settings Form */}
                            {currentGame.settingsForm && Object.entries(currentGame.settingsForm).length > 0 && (
                                <div className="settings-form">
                                    <h4>Параметры игры:</h4>
                                    {Object.entries(currentGame.settingsForm).map(([key, setting]) => (
                                        <div key={key} className="setting-item">
                                            <label htmlFor={`setting-${key}`}>{setting.name}:</label>
                                            <SettingsInput
                                                setting={{
                                                    ...setting,
                                                    value: settingsChanges[key] ?? setting.value ?? setting.default
                                                }}
                                                onChange={(value) => handleSettingChange(key, value)}
                                                disabled={gameState === "running"}
                                            />
                                        </div>
                                    ))}
                                    <button
                                        className="apply-settings-btn"
                                        onClick={handleApplySettings}
                                        disabled={gameState === "running" || Object.keys(settingsChanges).length === 0}
                                    >
                                        Применить параметры
                                    </button>
                                </div>
                            )}

                            {/* Start/Stop Buttons */}
                            <div className="game-controls">
                                <button
                                    className="start-btn"
                                    onClick={handleStartGame}
                                    disabled={gameState === "running" || startStopLoading}
                                >
                                    <FontAwesomeIcon icon={faPlay} /> Начать игру
                                </button>
                                <button
                                    className="stop-btn"
                                    onClick={handleStopGame}
                                    disabled={gameState !== "running" || startStopLoading}
                                >
                                    <FontAwesomeIcon icon={faStop} /> Остановить игру
                                </button>
                                <span className={`game-state ${gameState}`}>
                                    Состояние: {gameState}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
};
