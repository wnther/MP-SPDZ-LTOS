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
using namespace std;

#include <math.h>
#include <algorithm>


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
    string party_num = to_string(proc.P.my_num());
    ofstream filestream("party" + party_num + ".out");
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

    Temporary Insecure Preprocessing
    This works by having p1 generate two x,y randomly and calculating z based on its permutation and sending the data to p2
    The permutations are also hardcoded

*/


template<class T>
using open_t = typename T::open_type;

template<class T>
struct ShufflePrep {
    vector<open_t<T>> x_0;
    vector<open_t<T>> x_1;
    vector<open_t<T>> y_0;
    vector<open_t<T>> y_1;
    vector<open_t<T>> z_0;
    vector<open_t<T>> z_1;
};

template<class T>
using ShuffleVec = vector<vector<ShufflePrep<T>>>;


template <typename T>
ShuffleVec<T> send_preprocessing(SubProcessor<T>& proc, size_t input_size) {
    
    /*
        Temporary
        Hardcoded permutations
        Perm1 = 3 1 2 5 4
        Perm2 = 2 5 4 3 1
        Perm3 = 1 5 2 3 4
        Composite = 3 5 4 1 2
    */
    map<int, map<int, int>> perm_map = {
        {0, {{1, 3}, {2, 1}, {3, 2}, {4, 5}, {5, 4}}},
        {1, {{1, 2}, {2, 5}, {3, 4}, {4, 3}, {5, 1}}},
        {2, {{1, 1}, {2, 5}, {3, 2}, {4, 3}, {5, 4}}},
    };
    SeededPRNG G;

    auto &P = proc.P;
    size_t n = P.num_players();
    //auto &input = proc.input;
    size_t me = P.my_num();
    
    
    // auto allocate_shuffle_vec = [&](size_t n, size_t input_size) {
    //     return ShuffleVec<open_t<T>>(n, vector<vector<open_t<T>>>(n, vector<open_t<T>>(input_size)));
    // };
    
    
    // We need to generate random vectors of size input_size for x,y for each other party
    

    ShuffleVec<T> shuffle_matrix(n, vector<ShufflePrep<T>>(n));

    for (size_t j = 0; j < n; j++) {
        if (j == me) {
            continue; // No need to generate x y z pair with self
        }
        ShufflePrep<T> shuffle_prep = {
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
        };
        for (size_t i = 0; i < input_size; i++) {
            shuffle_prep.x_0[i] = G.get<open_t<T>>();
            shuffle_prep.x_1[i] = G.get<open_t<T>>();
            shuffle_prep.y_0[i] = G.get<open_t<T>>();
            shuffle_prep.y_1[i] = G.get<open_t<T>>();
        }
        
        // Generate z based on the permutation
        for (size_t i = 0; i < input_size; i++) {
            shuffle_prep.z_0[i] = shuffle_prep.x_0[perm_map.at(me).at(i+1)] - shuffle_prep.y_0[i];
            shuffle_prep.z_1[i] = shuffle_prep.x_1[perm_map.at(me).at(i+1)] - shuffle_prep.y_1[i];
        }

        shuffle_matrix[me][j] = shuffle_prep;

    }
    
    for (size_t i = 0; i < n; i++) {
        ShufflePrep<T> shuffle_prep = {
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
            vector<open_t<T>>(input_size),
        };
        shuffle_matrix[i][me] = shuffle_prep;
    }



    // send vectors x0 x1 y0 y1 (each size input_size (5))


    vector<octetStream> send(n);
    vector<octetStream> receive(n);

    for (size_t j = 0; j < n; j++) {
        if (j == me) continue; 

        for (size_t k = 0; k < input_size; k++) {
            shuffle_matrix[me][j].x_0[k].pack(send[j]);
            shuffle_matrix[me][j].x_1[k].pack(send[j]);
            shuffle_matrix[me][j].y_0[k].pack(send[j]);
            shuffle_matrix[me][j].y_1[k].pack(send[j]);
        }
        P.send_to(j, send[j]);
    }
    
    for (size_t i = 0; i < n; i++) {
        if (i == me) continue; 

        P.receive_player(i, receive[i]);
        for (size_t k = 0; k < input_size; k++) {
            shuffle_matrix[i][me].x_0[k].unpack(receive[i]);
            shuffle_matrix[i][me].x_1[k].unpack(receive[i]);
            shuffle_matrix[i][me].y_0[k].unpack(receive[i]);
            shuffle_matrix[i][me].y_1[k].unpack(receive[i]);
        }
    }

    return shuffle_matrix;
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
    (void) a;
    
    const auto n_shuffles = sizes.size();
    assert(sources.size() == n_shuffles);
    assert(destinations.size() == n_shuffles);
    assert(unit_sizes.size() == n_shuffles);
    assert(shuffles.size() == n_shuffles);
    assert(reverse.size() == n_shuffles);

    
    // Initialize the shuffles.
    vector is_exact(n_shuffles, false);
    
    vector<vector<T>> to_shuffle;
 
    clearprint_for_party(proc);
    println_for_party(proc, "Hello");


    
    ShuffleVec<T> shuffle_matrix = send_preprocessing(proc, 5);
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
        (void) a;
        (void) sizes;
        (void) sources;
        (void) unit_sizes;
        (void) to_shuffle;
        (void) is_exact;
    
        return 0;
}

template<class T>
void SecureShuffle<T>::finalize_multiple(StackedVector<T> &a, vector<size_t> &sizes, vector<size_t> &unit_sizes,
    vector<size_t> &destinations, vector<bool> &isExact, vector<vector<T>> &to_shuffle) {
        (void) a;
        (void) sizes;
        (void) unit_sizes;
        (void) destinations;
        (void) isExact;
        (void) to_shuffle;
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