#include "mol.h"

// copy the values into atom
void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{
    strcpy(atom->element, element);
    // printf("Atomset: atom->Element = %s  element = %s\n", atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

// copy the values in atom to x,y,z
void atomget(atom *atom, char element[3], double *x, double *y, double *z)
{
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

// copy a1,a2,epairs into bond
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{

    bond->a1 = *a1;
    // printf("b pass 0.1\n");

    bond->a2 = *a2;
    bond->epairs = *epairs;
    // printf("b pass 1\n");
    bond->atoms = *atoms;
    
    compute_coords(bond);
}

// copy bond attributes into a1, a2, epairs and atoms
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
    
    // for (int i = 0; i < sizeof(atoms)/sizeof(atom); i++)
    // {
    //     atomget(atoms[i], bond->atoms[i].element, &bond->atoms[i].x, &bond->atoms[i].y, &bond->atoms[i].z);
    // }    
}

// create and return a molecule
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{
    molecule *molecule;
    molecule = malloc(sizeof(*molecule));
    molecule->atom_max = atom_max;
    molecule->bond_max = bond_max;
    molecule->atom_no = 0;
    molecule->bond_no = 0;
    molecule->atoms = malloc(sizeof(struct atom) * atom_max);
    molecule->atom_ptrs = malloc(sizeof(struct atom *) * atom_max);
    molecule->bonds = malloc(sizeof(struct bond) * bond_max);
    molecule->bond_ptrs = malloc(sizeof(struct bond *) * bond_max);

    return molecule;
}

// coppy the values from src into a new molecule and return it
// still need to copy atoms, atom_ptrs, bonds, bond_ptrs
molecule *molcopy(molecule *src)
{
    molecule *mol;
    mol = molmalloc(src->atom_max, src->bond_max);

    for (int i = 0; i < src->atom_no; i++)
    {
        molappend_atom(mol, src->atoms);
    }

    for (int i = 0; i < src->bond_no; i++)
    {
        molappend_bond(mol, src->bonds);
    }
    return mol;
}


// free memory from ptr incuding the arrays atoms, atom_ptrs, bonds, bond_ptrs
void molfree(molecule *ptr)
{
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

// copy data from atom to the first empty atom in atoms array in molecule
void molappend_atom(molecule *molecule, atom *atom)
{
    if (molecule->atom_max == 0)
    {
        molecule->atom_max = 1;
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max);
    }
    else if (molecule->atom_no >= molecule->atom_max)
    {
        molecule->atom_max = molecule->atom_max * 2;
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max);
        for (int i = 0; i < molecule->atom_no; i++)
            molecule->atom_ptrs[i] = &molecule->atoms[i];
    }

    // printf("atom element: %s\n", atom->element);
    atomset(&molecule->atoms[molecule->atom_no], atom->element, &atom->x, &atom->y, &atom->z);
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no++;
    // molsort(molecule);
}

// copy data from atom to the first empty bond in bonds array in molecule
void molappend_bond(molecule *molecule, bond *bond)
{

    if (molecule->bond_max == 0)
    {
        molecule->bond_max = 1;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond *) * molecule->bond_max);
    }
    else if (molecule->bond_no >= molecule->bond_max)
    {
        molecule->bond_max = molecule->bond_max * 2;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond *) * molecule->bond_max);
        for (int i = 0; i < molecule->bond_no; i++)
            molecule->bond_ptrs[i] = &molecule->bonds[i];
    }
    bondset(&molecule->bonds[molecule->bond_no], &bond->a1, &bond->a2, &bond->atoms, &bond->epairs);
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no]; // check if line is correct
    molecule->bond_no++;
    // molsort(molecule);
}


void compute_coords(bond *bond)
{
    // printf("c pass here lol\n");
    atom *a1 = &bond->atoms[bond->a1];
    atom *a2 = &bond->atoms[bond->a2];
    // printf("c pass 0\n");
    // printf("c pass 1\n");
    
    // printf("%hu\n", bond->a1);
    // printf("c pass 2\n");
    bond->x1 = a1->x;
    // printf("c pass 3\n");
    bond->x2 = a2->x;
    // printf("c pass 4\n");
    bond->y1 = a1->y;
    // printf("c pass 5\n");
    bond->y2 = a2->y;
    
    bond->z = (a1->z + a2->z) / 2;
    bond->len = sqrt(((bond->x2 - bond->x1) * (bond->x2 - bond->x1)) + ((bond->y2 - bond->y1) * (bond->y2 - bond->y1)) );

    bond->dx = (bond->x2 - bond->x1)/bond->len;
    bond->dy = (bond->y2 - bond->y1) /bond->len;

    
    // printf("c pass 10\n");
}

int atom_comp(const void *a, const void *b)
{
    const atom *p1, *p2;
    p1 = *(atom **)a;
    p2 = *(atom **)b;
    double z = p1->z - p2->z;

    if(z > 0)
        return 1;
    else if(z < 0)
        return -1;
    else
        return 0;
}

int bond_comp(const void *a, const void *b)
{
    const bond *p1, *p2;
    p1 = *(bond **)a;
    p2 = *(bond **)b;

    double z = p1->z - p2->z;

    if(z > 0)
        return 1;
    else if(z < 0)
        return -1;
    else
        return 0;
    
    
}

// sort the atom_ptrs array in increasing z value
// sort bond_ptrs by average of z value of two atoms per bond
// use qsort
void molsort(molecule *molecule)
{
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), atom_comp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_comp);
}

// allocate compute and return an affine transformation matrix corresponding to a rotation of deg
// matrix must be freed by the user when no longer needed
void xrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180);
    double xRotationArray[3][3] = {{1, 0, 0}, {0, cos(rad), -sin(rad)}, {0, sin(rad), cos(rad)}};
    for(int i = 0; i < 3; i++)
        for(int j = 0; j < 3; j++)
            xform_matrix[i][j] = xRotationArray[i][j];
    
}

// affine transformation coresponding to deg
void yrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180);
    double yRotationArray[3][3] = {{cos(rad), 0, sin(rad)}, {0, 1, 0}, {-sin(rad), 0, cos(rad)}};

    for(int i = 0; i < 3; i++)
        for(int j = 0; j < 3; j++)
            xform_matrix[i][j] = yRotationArray[i][j];
}

// affine transformation coresponding to the deg
void zrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180);
    double zRotationArray[3][3] = {{cos(rad), -sin(rad), 0}, {sin(rad), cos(rad), 0}, {0, 0, 1}};

    for(int i = 0; i < 3; i++)
        for(int j = 0; j < 3; j++)
            xform_matrix[i][j] = zRotationArray[i][j];
    
}

int allValuesAreZero(xform_matrix xform_matrix, int rows, int cols) {
    float epsilon = 0.0001;

  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
        // printf("i[%d]j[%d] value[%f]\n", i,j, xform_matrix[i][j]);
        if (fabs(xform_matrix[i][j]) > epsilon) {
            // not equal to 0
            // printf("xform != 0\n");
            return 0;
        }
    }
  }
  return 1;
}

// apply transformation to matrix to all the atoms of the molecule
void mol_xform(molecule *molecule, xform_matrix xform_matrix)
{
    if(allValuesAreZero(xform_matrix, 3, 3) == 1){
        // printf("Entered 0\n");
        return;
    }

    // printf("passed\n");
    for(int i = 0; i < 3; i++){
        for(int j = 0; j < 3; j++){

        }
    }
    
    for (int i = 0; i < molecule->atom_no; i++)
    {
        atom *atom = &molecule->atoms[i];
        double x,y,z;

        x = xform_matrix[0][0] * atom->x + 
            xform_matrix[0][1] * atom->y +
            xform_matrix[0][2] * atom->z;

        y = xform_matrix[1][0] * atom->x +
            xform_matrix[1][1] * atom->y +
            xform_matrix[1][2] * atom->z;

        z = xform_matrix[2][0] * atom->x +
            xform_matrix[2][1] * atom->y +
            xform_matrix[2][2] * atom->z; 

        atom->x = x;
        atom->y = y;
        atom->z = z;
    }

    for(int i = 0; i < molecule->bond_no; i++)
    {
        compute_coords(&molecule->bonds[i]);
    }
    
}

// rotations *spin( molecule *mol ){
//     rotations* rotation = malloc(sizeof(rotations));
    


//     return rotation;
// }


// void rotationsfree( rotations *rotations ){
//     free(rotations->x);
//     free(rotations->y);
//     free(rotations->z);
//     free(rotations);
// }
