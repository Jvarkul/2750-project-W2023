#!/usr/bin/python3

import molecule

radius = {}
element_name = {}
radial_gradients = ""

header = """<svg version="1.1" class="viewMolecule" width="1000" height="1000" 
                    xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""
offsetx = 500
offsety = 500


class Atom():
    def __init__(self, c_atom): 
        self.element = c_atom.element
        self.x = c_atom.x
        self.y = c_atom.y
        self.z = c_atom.z

    def __str__(self):
        atom_sting = "z =", self.z #'   <circle x="%.2f" y="%.2f" z="%.2f" element="%s"/>' %(self.x, self.y, self.z, self.element)
        return atom_sting

    def svg(self):
        self.x = (self.x * 100) + offsetx
        self.y = (self.y * 100) + offsety
        
        
        radValue = radius[self.element]
        elementValue = element_name[self.element]

        svgString = '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' %(self.x, self.y, radValue, elementValue)
        return svgString
    
class Bond():
    def __init__(self, c_bond):
        self.a1 = c_bond.a1
        self.a2 = c_bond.a2
        self.epairs = c_bond.epairs
        self.atoms = c_bond.atoms
        self.x1 = c_bond.x1
        self.x2 = c_bond.x2
        self.y1 = c_bond.y1
        self.y2 = c_bond.y2
        self.z = c_bond.z
        self.len = c_bond.len
        self.dx = c_bond.dx
        self.dy = c_bond.dy
        
        
    def __str__(self):
        bond_string =  "z", self.z,  "x1", self.x1, "dx" , self.dx, "dy", self.dy, "len", self.len
        return bond_string

    def svg (self):
        dx = self.dx*10.0
        dy = self.dy*10.0
        
        x1s = ((self.x1 * 100) + offsetx) - dy 
        y1s = ((self.y1 * 100) + offsety) + dx
        x1b = ((self.x1 * 100) + offsetx) + dy
        y1b = ((self.y1 * 100) + offsety) - dx
        x2s = ((self.x2 * 100) + offsetx) + dy
        y2s = ((self.y2 * 100) + offsety) - dx
        x2b = ((self.x2 * 100) + offsetx) - dy
        y2b = ((self.y2 * 100) + offsety) + dx
        
        svgString = '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' %(x1s, y1s, x1b, y1b, x2s, y2s, x2b, y2b,)

        return svgString

class Molecule(molecule.molecule):
    
    # def __str__(self):
        
    #     mol_string = "atom_max" self.atom_max , "atom_no", self.atom_no,  "bond_max", self.bond_max, "bond_no = ", self.bond_no
    #     return mol_string
    
    
    def svg (self):
        header_string = header
        i = 0
        j = 0
        

        
        header_string += radial_gradients 
        
        # print(header_string)
        
        while i < self.atom_no and j < self.bond_no:
            
            a1 = Atom(self.get_atom(i))
            b1 = Bond(self.get_bond(j))
            
            if a1.z < b1.z:
                # print(a1.svg())
                header_string += a1.svg()
                i += 1
            else:
                # print(b1.svg())
                header_string += b1.svg()
                j += 1
            
            
        while i < self.atom_no:
            a1 = Atom(self.get_atom(i))
            # print(a1.svg())
            header_string += a1.svg()
            i += 1
            
        while j < self.bond_no:
            # print(b1.svg())
            b1 = Bond(self.get_bond(j))
            header_string += b1.svg()
            j += 1
           
        
        header_string += footer
        
        return header_string
    
    
    def parse(self, file):
        
        file.readline()
        file.readline()
        file.readline()

        line = file.readline()
        # print("line")
        # print(line)
        # print(type(line))
        item = line.split(' ')
        
        myList = list(filter(None, item))
        # print("myList")
        # print(myList)
        
        atom_no_string = myList[0]
        # print(atom_no_string)
        atom_max = int(atom_no_string)
        # print(atom_max)
        
        bond_no_string = myList[1]
        # print(bond_no_string)
        bond_max = int(bond_no_string)
        # print(bond_max)
    
        for i in range(0, atom_max):
        
            line = file.readline()
            myList = list(filter(None, line.split(' ')))
            print(myList)
            
            x = float(myList[0])
            y = float(myList[1])
            z = float(myList[2])
            element = str(myList[3])
            print(element, x,y,z)
            self.append_atom(element, x,y,z)

            
            
        for i in range(0, bond_max):
            line = file.readline()
            myList = list(filter(None, line.split(' ')))        
            print(myList)
            a1 = int(myList[0]) - 1
            a2 = int(myList[1]) - 1
            epairs = int(myList[2])
            print(a1, a2, epairs)
            self.append_bond(a1, a2, epairs)
        
        file.close()
    