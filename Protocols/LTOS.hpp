/*
 * SecureShuffle.hpp
 *
 */
#ifdef USING_EXPERIMENTAL_LTOS_SHUFFLING
#ifndef PROTOCOLS_SECURESHUFFLE_HPP_
#define PROTOCOLS_SECURESHUFFLE_HPP_

#include "SecureShuffle.h"
#include "Tools/Waksman.h"
#include <iostream>
#include <vector>

#include <math.h>
#include <algorithm>

/*

    Temporary
    Hardcoded permutations
    Perm1 = 3 1 2 5 4
    Perm2 = 2 5 4 3 1
    Perm3 = 1 5 2 3 4
    Composite = 3 5 4 1 2
*/


/*
    Printing to party specific file
*/

template <typename T>
ofstream get_party_stream(SubProcessor<T>& proc) {
    string party_num = to_string(proc.P.my_num());
    ofstream filestream("party" + party_num + ".out", std::ios::app);
    return filestream;
}

template <typename T>
void clearprint_for_party(SubProcessor<T>& proc) {
    ofstream filestream = get_party_stream(proc);
    filestream << "Party " << party_num << ":" << std::endl;
}


template <typename T>
void println_for_party(SubProcessor<T>& proc, const std::string& message) {
    ofstream filestream = get_party_stream(proc);
    filestream << message << std::endl;
}

template <typename T>
void println_for_party(SubProcessor<T>& proc, const std::vector<T>& vec) {
    ofstream filestream = get_party_stream(proc);
    for (const auto& v : vec) {
        filestream << v << " ";
    }
    filestream << std::endl;
}

template <typename T>
void println_for_party(SubProcessor<T>& proc, const StackedVector<T>& vec) {
    ofstream filestream = get_party_stream(proc);
    for (size_t i = 0; i < vec.size(); ++i)
        filestream << vec[i] << " ";
    filestream << std::endl;
}

/*
    Main Methods
*/


template<class T>
void ShuffleStore<T>::lock()
{
    store_lock.lock();
}

template<class T>
void ShuffleStore<T>::unlock()
{
    store_lock.unlock();
}

template<class T>
int ShuffleStore<T>::add()
{
    lock();
    int res = shuffles.size();
    shuffles.push_back({});
    unlock();
    return res;
}

template<class T>
typename ShuffleStore<T>::shuffle_type& ShuffleStore<T>::get(int handle)
{
    lock();
    auto& res = shuffles.at(handle);
    unlock();
    return res;
}

template<class T>
void ShuffleStore<T>::del(int handle)
{
    lock();
    shuffles.at(handle) = {};
    unlock();
}

template<class T>
SecureShuffle<T>::SecureShuffle(SubProcessor<T>& proc) :
        proc(proc)
{
}

template<class T>
SecureShuffle<T>::SecureShuffle(StackedVector<T>& a, size_t n, int unit_size,
        size_t output_base, size_t input_base, SubProcessor<T>& proc) :
        proc(proc)
{
    store_type store;
    int handle = generate(n / unit_size, store);

    vector<size_t> sizes{n};
    vector<size_t> unit_sizes{static_cast<size_t>(unit_size)};
    vector<size_t> destinations{output_base};
    vector<size_t> sources{input_base};
    vector<shuffle_type> shuffles{store.get(handle)};
    vector<bool> reverses{true};

    this->apply_multiple(a, sizes, destinations, sources, unit_sizes, shuffles, reverses);
}

template<class T>
void SecureShuffle<T>::apply_multiple(StackedVector<T>& a, vector<size_t>& sizes, vector<size_t>& destinations, vector<size_t>& sources,
                                    vector<size_t>& unit_sizes, vector<size_t>& handles, vector<bool>& reverse, store_type& store) {
    vector<shuffle_type> shuffles;
    for (size_t &handle : handles)
        shuffles.push_back(store.get(handle));

    this->apply_multiple(a, sizes, destinations, sources, unit_sizes, shuffles, reverse);
}

template<class T>
void SecureShuffle<T>::apply_multiple(StackedVector<T> &a, vector<size_t> &sizes, vector<size_t> &destinations,
    vector<size_t> &sources, vector<size_t> &unit_sizes, vector<shuffle_type> &shuffles, vector<bool> &reverse) {
    const auto n_shuffles = sizes.size();
    assert(sources.size() == n_shuffles);
    assert(destinations.size() == n_shuffles);
    assert(unit_sizes.size() == n_shuffles);
    assert(shuffles.size() == n_shuffles);
    assert(reverse.size() == n_shuffles);

    
    // Initialize the shuffles.
    vector is_exact(n_shuffles, false);
    
    vector<vector<T>> to_shuffle;
    prep_multiple(a, sizes, sources, unit_sizes, to_shuffle, is_exact);
    clearprint_for_party(proc);
    println_for_party(proc, "Hello");

    // Write the shuffled results into memory.
    finalize_multiple(a, sizes, unit_sizes, destinations, is_exact, to_shuffle);
    
    auto &P = proc.P;
    //auto &input = proc.input;
    
    vector<T> alice(P.num_players());
    vector<T> bob(P.num_players());
    
    // input.reset_all(P);
    // for (int i = 0; i < P.num_players(); i++)
    // input.add_from_all(i);
    // input.exchange();
    // for (int i = 0; i < P.num_players(); i++)
    // {
    //     alice[i] = input.finalize(0);
    //     bob[i] = input.finalize(1);
    // }
    
    // a[4] = alice[0];

    vector<octetStream> os(P.num_players());
    
    if (P.my_num() == 0)
    {
        P.receive_player(1, os[0]);
        alice[0].unpack(os[0]);
        ofstream st = get_party_stream(proc);
        st << "Alice a: " << alice[0] << std::endl;
    }
    else
    {
        ofstream st = get_party_stream(proc);
        st << "Bob a: " << a[0] << std::endl;
        a[0].pack(os[0]);
        P.send_to(0, os[0]);
    }

}


template<class T>
void SecureShuffle<T>::inverse_permutation(StackedVector<T> &stack, size_t n, size_t output_base,
                                           size_t input_base) {
    (void) stack;
    (void) n;
    (void) output_base;
    (void) input_base;
    
    // This is not needed for us.
    throw runtime_error("no");
}

template<class T>
int SecureShuffle<T>::prep_multiple(StackedVector<T> &a, vector<size_t> &sizes, 
    vector<size_t> &sources, vector<size_t> &unit_sizes, vector<vector<T>> &to_shuffle, vector<bool> &is_exact) {
    int max_depth = 0;
    const size_t n_shuffles = sizes.size();

    for (size_t currentShuffle = 0; currentShuffle < n_shuffles; currentShuffle++) {
        const size_t input_base = sources[currentShuffle];
        const size_t n = sizes[currentShuffle];
        const size_t unit_size = unit_sizes[currentShuffle];

        assert(n % unit_size == 0);

        const size_t n_shuffle = n / unit_size;
        const size_t n_shuffle_pow2 = (1u << int(ceil(log2(n_shuffle))));
        const bool exact = (n_shuffle_pow2 == n_shuffle) or not T::malicious;

        vector<T> tmp;
        if (exact)
        {
            tmp.resize(n_shuffle_pow2 * unit_size);
            for (size_t i = 0; i < n; i++)
                tmp[i] = a[input_base + i];
        }
        else
        {
            // Pad n_shuffle to n_shuffle_pow2. To reduce this back to n_shuffle after-the-fact, a flag bit is
            // added to every real entry.
            const size_t shuffle_unit_size = unit_size + 1;
            tmp.resize(shuffle_unit_size * n_shuffle_pow2);
            for (size_t i = 0; i < n_shuffle; i++)
            {
                for (size_t j = 0; j < unit_size; j++)
                    tmp[i * shuffle_unit_size + j] = a[input_base + i * unit_size + j];
                tmp[(i + 1) * shuffle_unit_size - 1] = T::constant(1, proc.P.my_num(), proc.MC.get_alphai());
            }
            for (size_t i = n_shuffle * shuffle_unit_size; i < tmp.size(); i++)
                tmp[i] = T::constant(0, proc.P.my_num(), proc.MC.get_alphai());
            unit_sizes[currentShuffle] = shuffle_unit_size;
        }

        to_shuffle.push_back(tmp);
        is_exact[currentShuffle] = exact;

        const int shuffle_depth = tmp.size() / unit_size;
        if (shuffle_depth > max_depth)
            max_depth = shuffle_depth;
    }

    return max_depth;
}

template<class T>
void SecureShuffle<T>::finalize_multiple(StackedVector<T> &a, vector<size_t> &sizes, vector<size_t> &unit_sizes,
    vector<size_t> &destinations, vector<bool> &isExact, vector<vector<T>> &to_shuffle) {
    const size_t n_shuffles = sizes.size();
    for (size_t currentShuffle = 0; currentShuffle < n_shuffles; currentShuffle++) {
        const size_t n = sizes[currentShuffle];
        const size_t shuffled_unit_size = unit_sizes[currentShuffle];
        const size_t output_base = destinations[currentShuffle];

        const vector<T>& shuffledData = to_shuffle[currentShuffle];

        if (isExact[currentShuffle])
            for (size_t i = 0; i < n; i++)
                a[output_base + i] = shuffledData[i];
        else
        {
            const size_t original_unit_size = shuffled_unit_size - 1;
            const size_t n_shuffle = n / original_unit_size;
            const size_t n_shuffle_pow2 = shuffledData.size() / shuffled_unit_size;

            // Reveal the "real element" flags.
            auto& MC = proc.MC;
            MC.init_open(proc.P);
            for (size_t i = 0; i < n_shuffle_pow2; i++) {
                MC.prepare_open(shuffledData.at((i + 1) * shuffled_unit_size - 1));
            }
            MC.exchange(proc.P);

            // Filter out the real elements.
            size_t i_shuffle = 0;
            for (size_t i = 0; i < n_shuffle_pow2; i++)
            {
                auto bit = MC.finalize_open();
                if (bit == 1)
                {
                    // only output real elements
                    for (size_t j = 0; j < original_unit_size; j++)
                        a.at(output_base + i_shuffle * original_unit_size + j) =
                                shuffledData.at(i * shuffled_unit_size + j);
                    i_shuffle++;
                }
            }
            if (i_shuffle != n_shuffle)
                throw runtime_error("incorrect shuffle");
        }
    }
}

template<class T>
vector<int> SecureShuffle<T>::generate_random_permutation(int n) {
    // TODO: This is Prep.Shuffles job
    
    vector<int> perm;
    int n_pow2 = 1 << int(ceil(log2(n)));
    int shuffle_size = n;
    for (int j = 0; j < n_pow2; j++)
        perm.push_back(j);
    SeededPRNG G;
    for (int i = 0; i < shuffle_size; i++) {
        int j = G.get_uint(shuffle_size - i);
        swap(perm[i], perm[i + j]);
    }

    return perm;
}

template<class T>
int SecureShuffle<T>::generate(int n_shuffle, store_type& store)
{
    (void) n_shuffle;
    
    int res = store.add();
    //auto& shuffle = store.get(res);

    return res;
}

template<class T>
vector<vector<T>> SecureShuffle<T>::configure(int config_player, vector<int> *perm, int n) {
    (void) config_player;
    (void) perm;
    (void) n;

    // This is not needed for us.
    throw runtime_error("no");
}

template<class T>
void SecureShuffle<T>::parallel_waksman_round(size_t pass, int depth, bool inwards, vector<vector<T>> &toShuffle,
    vector<size_t> &unit_sizes, vector<bool> &reverse, vector<shuffle_type> &shuffles)
{
    (void) pass;
    (void) depth;
    (void) inwards;
    (void) toShuffle;
    (void) unit_sizes;
    (void) reverse;
    (void) shuffles;

    // This is not needed for us.
    throw runtime_error("no");
}

template<class T>
vector<array<int, 5>> SecureShuffle<T>::waksman_round_init(vector<T> &toShuffle, size_t shuffle_unit_size, int depth, vector<vector<T>> &iter_waksman_config, bool inwards, bool reverse) {
    (void) toShuffle;
    (void) shuffle_unit_size;
    (void) depth;
    (void) iter_waksman_config;
    (void) inwards;
    (void) reverse;
    
    // This is not needed for us.
    throw runtime_error("no");

}

template<class T>
void SecureShuffle<T>::waksman_round_finish(vector<T> &toShuffle, size_t unit_size, vector<array<int, 5>> indices) {
    (void) toShuffle;
    (void) unit_size;
    (void) indices;
    
    // This is not needed for us.
    throw runtime_error("no");
}


#endif /* PROTOCOLS_SECURESHUFFLE_HPP_ */
#endif