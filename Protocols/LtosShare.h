#include "ShareInterface.h"
#include "Protocols/Share.h"

#ifndef PROTOCOLS_LTOSSHARE_H_
#define PROTOCOLS_LTOSSHARE_H_

template<class T> class LtosShare;

template<class T>
class LtosShare : public Share_<SemiShare<T>, SemiShare<T>>
{
    typedef LtosShare This;

public:
    typedef Share_<SemiShare<T>, SemiShare<T>> super;

    typedef T mac_key_type;
    typedef T mac_type;

    typedef LtosShare<typename T::next> prep_type;
    typedef LtosShare prep_check_type;
    typedef LtosShare bit_prep_type;
    typedef LtosShare input_check_type;
    typedef LtosShare input_type;
    typedef MascotMultiplier<LtosShare> Multiplier;
    typedef MascotTripleGenerator<prep_type> TripleGenerator;
    typedef T sacri_type;
    typedef typename T::Square Rectangle;
    typedef Rectangle Square;

    typedef MAC_Check_<LtosShare> MAC_Check;
    typedef Direct_MAC_Check<LtosShare> Direct_MC;
    typedef ::Input<LtosShare> Input;
    typedef ::PrivateOutput<LtosShare> PrivateOutput;
    typedef Beaver<This> BasicProtocol;
    typedef SPDZ<LtosShare> Protocol;
    typedef MascotFieldPrep<LtosShare> LivePrep;
    typedef MascotPrep<LtosShare> RandomPrep;
    typedef MascotTriplePrep<LtosShare> TriplePrep;
    typedef DummyMatrixPrep<This> MatrixPrep;

    static const bool expensive = true;

    static string type_short()
      { return string(1, T::type_char()); }

    static string type_string()
      { return "SPDZ " + T::type_string(); }

    LtosShare() {}
    template<class U>
    LtosShare(const U& other) : super(other) {}
    LtosShare(const SemiShare<T>& share, const SemiShare<T>& mac) :
            super(share, mac) {}
};

#endif