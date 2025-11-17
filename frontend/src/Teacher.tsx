import { useContext, type ReactNode, useState, useMemo, useEffect } from "react"
import { InfoContext } from "./info"
import { DataGrid, type Column, type SortColumn } from "react-data-grid"
import { api, socket } from "./api";
import { Status } from "./Status";
import { downloadFile } from "./utils";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCaretRight, faCircleNodes, faComputer, faGem, faGraduationCap, faPersonCircleMinus, faPlay, faStop, faUser } from "@fortawesome/free-solid-svg-icons";

interface Row {
    ip: string;
    pc: string;
    name: string;
    klads: number;
    action: ReactNode;
}

interface Student {
    pc: string,
    name: string,
    klads: number
}


export const Teacher = () => {
    const { status } = useContext(InfoContext);
    const [sortColumns, setSortColumns] = useState<readonly SortColumn[]>([]);
    const [students, setStudents] = useState<Record<string, Student>>({});

    useEffect(() => {
        const onstupdate = (data: Record<string, Student>) => {
            if (Object.keys(data).length != Object.keys(students).length) setSortColumns([]);
            setStudents(data)
        }
        socket.on("students", onstupdate)
        return () => {
            socket.off("students", onstupdate)
        }
    }, [students]);

    useEffect(() => { (async () => setStudents((await api.get("/students")).data))() }, [setStudents])

    // Column definitions with sortable columns marked
    const columns: readonly Column<Row>[] = [
        { key: "ip", name: <><FontAwesomeIcon icon={faCircleNodes} /> IP</> },
        { key: "pc", name: <><FontAwesomeIcon icon={faComputer} /> Компьютер</>, sortable: true },
        { key: "name", name: <><FontAwesomeIcon icon={faUser} /> Имя</>, sortable: true },
        { key: "klads", name: <><FontAwesomeIcon icon={faGem} /> Клады</>, sortable: true },
        { key: "action", name: <><FontAwesomeIcon icon={faCaretRight} /> Действо</> }
    ];

    const kick = async (ip: string) => {
        const t = (await api.post(`/students/kick/${ip}`)).data
        if (!t) alert("Ошибка при изгнании");
        else setStudents(t);

    }

    const mkrow = (ip: string, student: Student) => ({
        ip: ip, ...student, action: <button
            onMouseDown={e => e.stopPropagation()}
            onClick={() => kick(ip)}
        ><FontAwesomeIcon icon={faPersonCircleMinus} /> Изгнать</button>
    });

    const rows: readonly Row[] = Object.keys(students).map(t => mkrow(t, students[t]));
    // const rows: readonly Row[] = Array.from({length:31}, ()=>({pc:"a", name:"Иван Иванов, Иван Иванов", klads:4})).map(t=>mkrow("ip", t))

    // Apply sorting to rows when sort columns change
    const sortedRows = useMemo((): readonly Row[] => {
        if (sortColumns.length === 0) return rows;

        return [...rows].sort((a, b) => {
            for (const sort of sortColumns) {
                const comparator = getComparator(sort.columnKey);
                const compResult = comparator(a, b);
                if (compResult !== 0) {
                    return sort.direction === "ASC" ? compResult : -compResult;
                }
            }
            return 0;
        });
    }, [rows, sortColumns]);

    const buttonText = status == "run" ? <><FontAwesomeIcon icon={faStop} /> Остановить игру</> : <><FontAwesomeIcon icon={faPlay} /> Начать игру</>

    const gameAction = async () => {
        if (status == "reg") {
            setStudents((await api.post("/game/start")).data);
        } else {
            const d = (await api.post("/game/stop")).data;
            downloadFile("SchoolLinux-results.csv", d);
        }
    }

    return <>
        <h1><FontAwesomeIcon icon={faGraduationCap} /> Ученики</h1>
        <DataGrid
            columns={columns}
            rows={sortedRows}
            sortColumns={sortColumns}
            onSortColumnsChange={setSortColumns}
        />
        <Status />
        <button onClick={gameAction}>{buttonText}</button>
    </>
}

// Comparator function for different column types
function getComparator(sortColumn: string): (a: Row, b: Row) => number {
    switch (sortColumn) {
        case "name":
        case "pc":
            return (a, b) => a[sortColumn].localeCompare(b[sortColumn]); // String comparison
        case "klads":
            return (a, b) => a.klads - b.klads; // Numeric comparison
        default:
            return () => 0; // No sorting for other columns
    }
}