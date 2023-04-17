import sqlite3
import os
import MolDisplay

class Database():
    
    # INITILIZE DATABASE
    def __init__(self, reset=False):
        if reset is True and os.path.exists('molecules.db'):
            os.remove( 'molecules.db' )
            
        
        self.conn = sqlite3.connect("molecules.db")
        self.create_tables()
        
    # CREATE SQL TABLES
    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements(
                                ELEMENT_NO      INTEGER,
                                ELEMENT_CODE    VARCHAR(3),
                                ELEMENT_NAME    VARCHAR(32),
                                COLOUR1         CHAR(6),
                                COLOUR2         CHAR(6),
                                COLOUR3         CHAR(6),
                                RADIUS          DECIMAL(3),
                                PRIMARY KEY (ELEMENT_CODE)
                                );""")
        
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                          (
                                ATOM_ID         INTEGER     NOT NULL    PRIMARY KEY AUTOINCREMENT,
                                ELEMENT_CODE    VARCHAR(3),
                                X               DECIMAL(7,4),
                                Y               DECIMAL(7,4),
                                Z               DECIMAL(7,4),
                                FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements);""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                            (
                                BOND_ID         INTEGER     NOT NULL    PRIMARY KEY AUTOINCREMENT,
                                A1              INTEGER     NOT NULL,
                                A2              INTEGER     NOT NULL,
                                EPAIRS          INTEGER     NOT NULL);""")
            
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                            (
                                MOLECULE_ID     INTEGER     NOT NULL    PRIMARY KEY AUTOINCREMENT,
                                NAME            TEXT        NOT NULL    UNIQUE
                                );""")
            
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                            (
                                MOLECULE_ID     INTEGER     NOT NULL,
                                ATOM_ID         INTEGER     NOT NULL,
                                PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                                FOREIGN KEY (ATOM_ID) REFERENCES Atoms (ATOM_ID)
                                );""")
        
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                            (
                                MOLECULE_ID     INTEGER     NOT NULL,
                                BOND_ID         INTEGER     NOT NULL,
                                PRIMARY KEY (MOLECULE_ID, BOND_ID),
                                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                                FOREIGN KEY (BOND_ID) REFERENCES Bonds (BOND_ID)
                                );""")
        
    
    # This method should provide a method to use indexing (i.e. [key]) to 
    # set the values in the table named table based on the values in the tuple values (see example code, below).
    def __setitem__(self, table, values):
        cursor = self.conn.cursor()
        temp = ",".join(["?" for _ in range (len(values))])
        value = f"INSERT OR REPLACE INTO {table} VALUES ({temp})"
        cursor.execute(value, values)
        self.conn.commit()
        
    def delete_element(self, element):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Elements WHERE ELEMENT_CODE = (?)", (element,))
        self.conn.commit()
    # ADD ATOM TO SLQ TABLE
    def add_atom(self, molname, atom):
    
        element = atom.element
        x = atom.x
        y = atom.y
        z = atom.z
        cursor = self.conn.cursor()
        cursor.execute("SELECT ELEMENT_CODE FROM Elements WHERE ELEMENT_CODE=?",(element,))
        
        cursor.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?,?,?,?)",(element,x,y,z,))
        self.conn.commit()
        
        atomID = cursor.lastrowid
        
        cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        
        molID = cursor.fetchone()[0]

        cursor.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?,?)",(molID, atomID,))
        
        self.conn.commit()
        
    
    # ADD BOND TO SQL TABLE
    def add_bond(self, molname, bond):
        a1 = bond.a1
        a2 = bond.a2
        epairs = bond.epairs
        
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Bonds (A1,A2,EPAIRS) VALUES (?,?,?)",(a1,a2,epairs,))
        self.conn.commit()
        
        bondID = cursor.lastrowid
        
        
        cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        molID = cursor.fetchone()[0]
        
        cursor.execute("INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?,?)",(molID,bondID,))
        self.conn.commit()
        
    
    # APPEND ATOMS AND BONDS TO A NEW MOLECULE
    def add_molecule(self, name, fp):
        mol = MolDisplay.Molecule()        
        mol.parse(fp)
        print("adding molecule")
        print(mol.atom_no, mol.bond_no, mol.atom_max, mol.bond_max)
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Molecules (NAME) VALUES (?)", (name,))
        
        for i in range(0,mol.atom_no):
            self.add_atom(name, mol.get_atom(i))
            
        for i in range(0, mol.bond_no):
            self.add_bond(name, mol.get_bond(i))
    
        fp.close()
        
        
    # INSERT ATOM AND BOND DATA INTO A NEW MOLECULE
    def load_mol(self, name):
        MolDisplay.radius = self.radius()
        MolDisplay.element_name = self.element_name()
        MolDisplay.radial_gradients = self.radial_gradients()
        
        mol = MolDisplay.Molecule()
        
        cursor = self.conn.cursor()
        cursor.execute('''SELECT ELEMENT_CODE,X,Y,Z FROM 
                Molecules INNER JOIN MoleculeAtom ON 
                Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                INNER JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                WHERE Molecules.NAME = (?)''', (name,))
        
        temp = cursor.fetchall()
        for i in range (0, len(temp)):
            element = temp[i][0]
            x = temp[i][1]
            y = temp[i][2]
            z = temp[i][3]
            # print(element,x,y,z)
            mol.append_atom(element,x,y,z)
            
        cursor.execute('''SELECT A1,A2,EPAIRS FROM 
                Molecules INNER JOIN MoleculeBond ON 
                Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                INNER JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                WHERE Molecules.NAME = (?)''', (name,))
        temp = cursor.fetchall()
        for i in range (0, len(temp)):
            a1 = temp[i][0]
            a2 = temp[i][1]
            epairs = temp[i][2]
            # print(a1,a2,epairs)
            mol.append_bond(a1,a2,epairs)
            
        return mol
        
        
    # MAP ELEMENT_CODE TO RADIUS DICTIONARY
    def radius(self):
        radDic = {}                                 # radius dictionary
        cursor = self.conn.cursor()
        cursor.execute('''SELECT ELEMENT_CODE, RADIUS FROM Elements''')
        temp = cursor.fetchall()
        # print("radius")
        # print(temp)
        for i in range (0, len(temp)):
            radDic[temp[i][0]] = temp[i][1]
        # send radius to molDisplay
        return radDic
        
    # MAP ELEMENT_CODE TO ELEMENT_NAME IN A DICTIONARY
    def element_name(self):
        nameDic = {}
        cursor = self.conn.cursor()
        cursor.execute('''SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements''')
        temp = cursor.fetchall()
        # print("element_name")
        # print(temp)
        for i in range (0, len(temp)):
            nameDic[temp[i][0]] = temp[i][1]
        
        return nameDic
    
    
    # Create the gradiant to add to the header of the svg
    def radial_gradients(self):
        svgString = ""
        cursor = self.conn.cursor()
        cursor.execute('''SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements''')
        temp = cursor.fetchall()
        # print("radial_gradients")
        # print(temp)
        for i in range(0, len(temp)):
            name = temp[i][0]
            colour1 = temp[i][1]
            colour2 = temp[i][2]
            colour3 = temp[i][3]
            radialGradientSVG = """ 
                                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                                <stop offset="0%%" stop-color="#%s"/>
                                <stop offset="50%%" stop-color="#%s"/>
                                <stop offset="100%%" stop-color="#%s"/>
                                </radialGradient>""" % (name,colour1,colour2,colour3)
            svgString += radialGradientSVG
        
        return svgString

    # def do_GET(self):
        
    #     cursor = self.conn.cursor()
        
    #     # Execute a SELECT statement to retrieve data from the database
    #     cursor.execute("SELECT * FROM mytable")
    #     data = cursor.fetchall()
        
    #     # Format the data as HTML
    #     html = "<html><body><table>"
    #     for row in data:
    #         html += "<tr>"
    #         for column in row:
    #             html += "<td>" + str(column) + "</td>"
    #         html += "</tr>"
    #     html += "</table></body></html>"
        
    #     # Send the HTML response to the client
    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/html')
    #     self.end_headers()
    #     self.wfile.write(html.encode())
        
    #     # Close the database connection
    #     cursor.close()
        