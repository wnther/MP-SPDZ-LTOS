#include "SPDZ.hpp"

#include "Protocols/MascotPrep.hpp"
#include "Processor/FieldMachine.hpp"
#include "Math/gfp.hpp"
#include "Protocols/LtosShare.h"

template class FieldMachine<Share, Share, DishonestMajorityMachine>;
template class FieldMachine<LtosShare, LtosShare, DishonestMajorityMachine>;

template class Machine<Share<gfp_<0, 2>>, Share<gf2n>>;
template class Machine<LtosShare<gfp_<0, 2>>, LtosShare<gf2n>>;
