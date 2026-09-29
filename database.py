import aiosqlite

DB = "library.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            units INTEGER DEFAULT 0,
            year INTEGER DEFAULT 0,
            semester TEXT DEFAULT '',
            prerequisite TEXT DEFAULT ''
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            file_id TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
        """)
        await db.commit()

async def subjects():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id,name,units,year,semester,prerequisite FROM subjects ORDER BY year, name")
        return await cur.fetchall()

async def subject(subject_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id,name,units,year,semester,prerequisite FROM subjects WHERE id=?", (subject_id,))
        return await cur.fetchone()

async def add_subject(name, units=0, year=0, semester="", prerequisite=""):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "INSERT INTO subjects(name,units,year,semester,prerequisite) VALUES(?,?,?,?,?)",
            (name,units,year,semester,prerequisite)
        )
        await db.commit()
        return cur.lastrowid

async def add_resource(subject_id, category, title, file_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO resources(subject_id,category,title,file_id) VALUES(?,?,?,?)",
            (subject_id,category,title,file_id)
        )
        await db.commit()

async def resources(subject_id, category):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id,title,file_id FROM resources WHERE subject_id=? AND category=? ORDER BY id DESC",
            (subject_id,category)
        )
        return await cur.fetchall()
