"""Python-based Simulations Chemistry Framework"""

'''
This will use the PySCF framework to perform 
electronic structure calculations.
'''
import numpy as np
from ase.calculators.calculator import (Calculator, CalculatorError, 
                    CalculatorSetupError, all_changes, all_properties)



def ase_atoms_to_pyscf(ase_atoms):
    '''Convert ASE atoms to PySCF atom.

    Note: ASE atoms always use A.
    '''
    return [[atom.symbol, atom.position] for atom in ase_atoms]

atoms_from_ase = ase_atoms_to_pyscf


class PySCF(Calculator):
    implemented_properties = ['energy']

    def __init__(self, restart=None, ignore_bad_restart_file=False,
                 label='PySCF', atoms=None, scratch=None, **kwargs):
        """Construct PySCF-calculator object.

        Parameters
        ==========
        label: str
            Prefix to use for filenames (label.in, label.txt, ...).
            Default is 'PySCF'.

        mfclass: PySCF mean-field class
        molcell: PySCF :Mole: or :Cell:
        """
        Calculator.__init__(self, restart=None, ignore_bad_restart_file=False,
                            label='PySCF', atoms=None, scratch=None, **kwargs)

        # TODO
        # This explicitly refers to "cell". How to refer
        # to both cell and mol together?

        self.mf=None
        self.initialize(**kwargs)

    # Check if ASE molecule begins with A or a
    def initialize(self, molcell, mf_class, mf_dict):
        if not molcell.unit.startswith(('A','a')):
            raise RuntimeError("PySCF unit must be A to work with ASE")

        self.molcell=molcell
        self.mf_class=mf_class
        self.mf_dict=mf_dict

    def set(self, **kwargs):
        changed_parameters = Calculator.set(self, **kwargs)
        if changed_parameters:
            self.reset()

    # Call ASE base calculator and calculate energy
    def calculate(self, atoms=None, properties=['energy'],
                  system_changes=['positions', 'numbers', 'cell',
                                  'pbc', 'charges','magmoms']):

        Calculator.calculate(self, atoms)

        calc_molcell = self.molcell.copy()
        calc_molcell.atom = ase_atoms_to_pyscf(atoms)
        calc_molcell.a = np.asarray(atoms.cell)
        calc_molcell.build(None,None)
        self.mf = self.mf_class(calc_molcell)
        for key in self.mf_dict:
            self.mf.__dict__[key] = self.mf_dict[key]

        self.results['energy']=self.mf.scf()
        self.results['mf']=self.mf

def make_kpts(cell, nks):
    raise DeprecationWarning('Use cell.make_kpts(nks) instead.')


