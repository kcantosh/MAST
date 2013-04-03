############################################################################
# MAterials Simulation Toolbox (MAST)
# Version: January 2013
# Programmers: Tam Mayeshiba, Tom Angsten, Glen Jenness, Hyunwoo Kim,
#              Kumaresh Visakan Murugan, Parker Sear
# Created at the University of Wisconsin-Madison.
# Replace this section with appropriate license text before shipping.
# Add additional programmers and schools as necessary.
############################################################################
import os

import numpy as np
import pymatgen as pmg

from MAST.utility import InputOptions
from MAST.utility import MASTObj
from MAST.utility import MASTError

ALLOWED_KEYS = {\
                 'inputfile'    : (str, 'mast.inp', 'Input file name'),\
               }

MAST_KEYWORDS = ['program',
                 'system_name',
                 'scratch_directory',
                ]

structure_KEYWORDS = ['posfile', # str
                     'atom_list', # str
                     'spacegroup', # int
                     'symmetry_only', # bool
                     'coord_type', # str
                    ]

UNITCELL_KEYWORDS = ['lattice_constant',
                     'a',
                     'b',
                     'c',
                     'alpha',
                     'beta',
                     'gamma',
                    ]

DEFECTS_KEYWORDS = ['coord_type',
                    'vacancy',
                    'interstial',
                    'antisite',
                   ]

PROGRAM_KEYWORDS = ['singlepoint',
                    'optimization',
                    'neb',
                   ]

RECIPE_KEYWORDS = ['recipe',
                  ]

class InputParser(MASTObj):
    """Parses input file and returns the options.
    """
    def __init__(self, **kwargs):
        MASTObj.__init__(self, ALLOWED_KEYS, **kwargs)
        self.section_end = '$end'
        self.delimeter = ' ' # how we're breaking up each line
        self.section_parsers = {\
                                    'mast'     : self.parse_mast_section,
                                    'structure' : self.parse_structure_section,
                                    'unitcell' : self.parse_unitcell_section,
                                    'ingredients'  : self.parse_ingredients_section,
                                    'defects'  : self.parse_defects_section,
                                    'recipe'   : self.parse_recipe_section,
#                                    'neb'      : self.parse_neb_section,
                               }

    def parse(self):
        """Parses information from the input file"""
#        print 'Calling current InputParser'
        options   = InputOptions()
        infile    = file(self.keywords['inputfile'])
        contents  = infile.read()
        infile.close()

        sections  = contents.strip().split(self.section_end)[:-1]
        for section_content in sections:
            section_content = section_content.strip()
#            print '\n\nDEBUG: section_content:', section_content
#            if not section_content:
#                continue

            section_content = section_content.split('\n')
            section_content = [line for line in section_content if not (line.startswith('#') or \
                                                                        line.startswith('!'))]
            section_name = section_content[0][1:]

            print 'section name:', section_name # For testing
            if section_name not in self.section_parsers:
                error = 'Section %s not recognized' % section_name
                MASTError(self.__class__.__name__, error)
                return

#            index = len(section_name) + 1
            self.section_parsers[section_name](section_name, section_content[1:], options)

#        print options
        return options

    def parse_mast_section(self, section_name, section_content, options):
        """Parse the mast section and populate the options"""
        section_options = dict()

#        section_content = section_content.split('\n')

        for line in section_content:
            line = line.split(self.delimeter)

            if (line[0] not in MAST_KEYWORDS):
                error = 'Section keyword %s not recognized' % line[0]
                MASTError(self.__class__.__name__, error)
                return
            else:
                section_options[line[0]] = line[1]
                options.set_item(section_name, line[0], line[1])

#        print 'In parse_mast_section:', options.get_item(section_name, 'system_name')

    def parse_structure_section(self, section_name, section_content, options):
        """Parse the structure section and populate the options

            Format is:
                atom_symbol x y z

            For now, assume positions are in Cartesian
        """
        coordinates = list()
        atom_list = list()
        coord_type = 'cartesian'
        posfile = None

#        section_content = section_content.split('\n')

        for line in section_content:
            line = line.split(self.delimeter)

            if (line[0] == 'coord_type'):
                coord_type = line[1]
            elif (line[0] == 'posfile'):
                posfile = line[1]
            else:
                atom_list.append(line[0])
                coordinates.append(line[1:])

#        print coordinates
        coordinates = np.array(coordinates, dtype='float')

        options.set_item(section_name, 'coord_type', coord_type)
        options.set_item(section_name, 'coordinates', coordinates)
        options.set_item(section_name, 'atom_list', atom_list)
        options.set_item(section_name, 'posfile', posfile)

    def parse_unitcell_section(self, section_name, section_content, options):
        """Parse the unit cell section and populate the options

            By default this will assume that the cell is given as:
                a11 a12 a13
                a21 a22 a23
                a31 a32 a33
           However, it can also read in the following format (TO BE DONE!):
               a = xxx
               b = yyy
               c = zzz
               alpha = xx 
               beta = yy
               gamma = zz

           Based off of this information, this section will construct a pymatgen Lattice object
        """
        cell = list()

#        section_content = section_content.split('\n')

        for line in section_content:
            line = line.split(self.delimeter)
            cell.append(line)

        cell = np.array(cell, dtype='float')

        options.set_item(section_name, 'lattice', pmg.Lattice(cell))

    def parse_defects_section(self, section_name, section_content, options):
        """Parse the defects section and populate the options.

        """
        defect_types = dict()
#        section_content = section_content.split('\n')

        count = 0
        for line in section_content:
            type_dict = dict()

            line = line.split(self.delimeter)

            if (line[0] == 'coord_type'):
                defect_types['coord_type'] = line[1]
            else:
                coord = line[1:-1]

                type_dict['type'] = line[0]
                type_dict['coordinates'] = np.array(coord, dtype='float')
                type_dict['symbol'] = line[-1]

                defect_types['defect%i' % count] = type_dict

                count += 1

        if ('coord_type' not in defect_types):
            defect_types['coord_type'] = 'cartesian'

        options.set_item(section_name, 'num_defects', count)
        options.set_item(section_name, 'defects', defect_types)

    def parse_recipe_section(self, section_name, section_content, options):
        """Parse the recipe section and populate the options"""
#        section_content = section_content.split('\n')

        for line in section_content:
            line = line.split(self.delimeter)
            if (line[0] == 'recipe'):
                try:
                    recipe_path = os.environ['MAST_RECIPE_PATH']
                except KeyError:
                    error = 'MAST_RECIPE_PATH environment variable not set'
                    MASTError(self.__class__.__name__, error)
 
                recipe_file = '%s/%s' % (recipe_path, line[1])
                options.set_item(section_name, 'recipe_file', recipe_file)
#        print 'DEBUG: recipe_path =', recipe_path
#        print 'DEBUG: recipe_file =', recipe_file

    def parse_ingredients_section_old(self, section_name, section_content, options):
        """Parse the ingredients section and populate the options

            THIS IS NOW DEPECATED, DO NOT USE.  WILL GET REMOVED LATER.
        """

        section_content = section_content.split('\n')

        for line in section_content:
            ingredient_dict = dict()
            line = line[:-1].split('(')
            program_options = line[1].split(',')
            temp_dict = dict()

            for opt in program_options:
                opt = opt.split('=')
                temp_dict[opt[0]] = opt[1]

            options.set_item(section_name, line[0].lower(), temp_dict)

    def parse_ingredients_section(self, section_name, section_content, options):
        """Parse the ingredients section and populate the options
            Section takes the form of:
                $ingredients
                begin ingredients_global
                kpoints 3x3x3
                xc pbe
                end

                begin singlepoint
                encut 400
                end

                begin optimize
                encut 300
                ibrion 2
                end

                $end

            kpoints are parsed out as a 3 index list of integers, everything else is parsed out
            as a string.

            Anything in ingredients_global are then appended onto each individual ingredient.
        """

        global_dict = dict()
        ingredients_dict = dict()

        for line in section_content:
            if (line.startswith('#') or line.startswith('!') or (not line)):
# Check for comments starting with a # or a !, or just a good ol' fashioned blank line
                continue
            elif (line.startswith('begin')):
# Each ingredient section starts with "begin", check for this line, and initialize the individual
# ingredient dictionary
                ingredient_name = line.split()[1]
                ingredient_dict = dict()
            elif ('end' not in line):
                opt = line.split()
#                print opt
                if (opt[0] == 'kpoints'):
                    kpts = map(int, opt[1].split('x'))
                    ingredient_dict[opt[0]] = kpts
                else:
                    ingredient_dict[opt[0]] = opt[1]
            elif ('end' in line):
# Each ingredient section ends with "end", if present finish that current section and assign
# the neccessary element in the ingredients dictionary and create the global dictionary
                if (ingredient_name == 'ingredients_global'):
                    global_dict = ingredient_dict
                else:
                    ingredients_dict[ingredient_name] = ingredient_dict

# Here we append the global dictionary that has been defined from above
        for key, value in ingredients_dict.items():
            value.update(global_dict)
            options.set_item(section_name, key, value)

#        print 'DEBUG: ingredients_dict =', ingredients_dict
