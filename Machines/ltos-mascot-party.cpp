#define USING_EXPERIMENTAL_LTOS_SHUFFLING 1
#include "Math/gfp.hpp"
#include "GC/TinierSecret.h"
#include "Processor/FieldMachine.h"
#include "Protocols/LtosShare.h"


int main(int argc, const char** argv)
{
    ez::ezOptionParser opt;
    DishonestMajorityFieldMachine<LtosShare>(argc, argv, opt);
}
