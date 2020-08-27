import math

class Messages:

    MSG_OUT_FORMAT_NOT_SUPPORTED = 'Output file format is not supported.'
    MSG_INSTANCE_FILE_NOT_FOUND = 'Instance file not found.'
    MSG_INPUT_FORMAT_NOT_SUPPORTED = 'Input file format is not supported.'
    MSG_INPUT_WRONG_INDEX = 'You have entered a wrong index.'
    MSG_MODEL_READ_FILE_ONLY_ONCE = 'The Model can read the file only once.'
    MSG_MODEL_NO_PARSING_FOR_FORMAT = 'Parsing for the format is not implemented.'
    MSG_NO_MPL_MODEL_CANNOT_SOLVE = 'Model cannot be solved because mpl_model does not exist (see which files were used as input).'
    MSG_NO_MPL_MODEL_CANNOT_SAVE = 'Model cannot be saved because mpl_model does not exist (see which files were used as input).'
    MSG_FILE_SHOULD_BE_PATH = 'The file attribute should have type Path().'
    MSG_STOCH_ONLY_TO_MPS = 'Stochastic models are to be converted only to .cor, .sto, .tim (SMPS)'
    MSG_EXPLICIT_IN_MPS = '''
    The model formulated in .mpl / .mps file is not compatible with the PNB solver.\n
    First stage constraints in .mpl should be defined before the second stage constraints.\n
    Otherwise, .tim file has a wrong format (SCENARIOS EXPLICIT) and the solver mixes up 1st, 2nd stage constraints.'''

class Numbers:

    INT_BIG_NUMBER = 100000000000000000000