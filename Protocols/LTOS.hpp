/*
 * SecureShuffle.hpp
 *
 */

 
#ifdef USING_EXPERIMENTAL_LTOS_SHUFFLING
#ifndef PROTOCOLS_SECURESHUFFLE_HPP_
#define PROTOCOLS_SECURESHUFFLE_HPP_

#include "Tools/CheckVector.h"
#include "SecureShuffle.h"
#include "Tools/Waksman.h"
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <map>

using namespace std;

#include <math.h>
#include <algorithm>

/*
    For Experimentation
*/

static inline unsigned int mylog2 (unsigned int val) {
    if (val == 0) return UINT_MAX;
    if (val == 1) return 0;
    unsigned int ret = 0;
    while (val > 1) {
        val >>= 1;
        ret++;
    }
    return ret;
}

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

/*

    (Possibly) Temporary Insecure Preprocessing
    This works by having p1 generate two x,y randomly and calculating z based on its permutation and sending the data to p2
    The permutations are also hardcoded

*/
template <typename T>
ShuffleVec<T> conduct_preprocessing(SubProcessor<T>& proc, size_t input_size, vector<int> perm_map) {
    SeededPRNG G;
    auto &P = proc.P;
    size_t n = P.num_players();
    size_t me = P.my_num();
    
    // We need to generate random vectors of size input_size for x,y for each other party
    ShuffleVec<T> shuffle_matrix(n, vector<ShufflePrep<T>>(n));

    for (size_t j = 0; j < n; j++) {
        if (j == me) continue; // No need to generate x y z pair with self

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
            shuffle_prep.z_0[i] = shuffle_prep.x_0[perm_map.at(i)] - shuffle_prep.y_0[i];
            shuffle_prep.z_1[i] = shuffle_prep.x_1[perm_map.at(i)] - shuffle_prep.y_1[i];
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

    // send vectors x0 x1 y0 y1 (each size input_size)
    size_t batch_size = 65536;
    size_t num_batches = (input_size + batch_size - 1) / batch_size;

    for (size_t current_batch = 0; current_batch < num_batches; current_batch++) {
        vector<octetStream> send(n);
        vector<octetStream> receive(n);
        size_t start = current_batch * batch_size;
        size_t end = min(start + batch_size, input_size);

        for (size_t j = 0; j < n; j++) {
            if (j == me) continue; 
    
            for (size_t k = start; k < end; k++) {
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
            for (size_t k = start; k < end; k++) {
                shuffle_matrix[i][me].x_0[k].unpack(receive[i]);
                shuffle_matrix[i][me].x_1[k].unpack(receive[i]);
                shuffle_matrix[i][me].y_0[k].unpack(receive[i]);
                shuffle_matrix[i][me].y_1[k].unpack(receive[i]);
            }
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
    
    auto start = chrono::high_resolution_clock::now();


    const auto n_shuffles = sizes.size();
    assert(sources.size() == n_shuffles);
    assert(destinations.size() == n_shuffles);
    assert(unit_sizes.size() == n_shuffles);
    assert(shuffles.size() == n_shuffles);
    assert(reverse.size() == n_shuffles);

    auto source_offset = sources[0];

    size_t input_size = sizes[0];
    
    // Preprocessing (Offline)
    vector<int> perm_map = generate_random_permutation(input_size);
    ShuffleVec<T> shuffle_matrix = conduct_preprocessing(proc, input_size, perm_map);
    // Main part of the protocol (Online)
    auto &P = proc.P;
    size_t n = P.num_players();
    size_t me = P.my_num();

    vector<T> to_shuffle = vector<T>(input_size);
    vector<T> old = vector<T>(input_size);
    for (size_t i = 0; i < input_size; i++) {
        to_shuffle[i] = a[source_offset + i];
        old[i] = a[source_offset + i];
    }

    auto start1 = chrono::high_resolution_clock::now();
    for (size_t i = 0; i < n; i++) {
        if (i == me) {
            vector<vector<T>> rs(n, vector<T>(input_size));

            //Calculate r,s (Step ii in the paper)
            vector<octetStream> receive(n);
            for (size_t j = 0; j < n; j++) {
                if (j == me) continue; 
                P.receive_player(j, receive[j]);
            }

            for (size_t j = 0; j < n; j++) {
                if (j == me) continue;
                vector<T> temp_input_vec(input_size);
                vector<T> temp_output_vec(input_size);

                for (size_t q = 0; q < input_size; q++) {
                    temp_input_vec[q].unpack(receive[j]);
                }

                for (size_t q = 0; q < input_size; q++) {
                    SemiShare<open_t<T>> temp_share(shuffle_matrix[me][j].z_0[q]);
                    SemiShare<open_t<T>> temp_mac(shuffle_matrix[me][j].z_1[q]);
                    T z_ltos_share(temp_share, temp_mac);
                    temp_output_vec[q] = temp_input_vec[perm_map.at(q)] + z_ltos_share;
                }

                rs[j] = temp_output_vec;
            }

            // Calculate own r,s (Step b in the paper)
            rs[me] = vector<T>(input_size);
            for (size_t q = 0; q < input_size; q++) {
                rs[me][q] = to_shuffle[perm_map.at(q)];
            }
            
            // Define shares for next round (Step c in the paper)
            for (size_t q = 0; q < input_size; q++) {
                to_shuffle[q] = rs[0][q];
                for (size_t j = 1; j < n; j++) {
                    to_shuffle[q] += rs[j][q];
                }
            }
        }
        else {
            //Calculate and send w (Step i in the paper)
            vector<T> w(input_size);
            
            auto x_0 = shuffle_matrix[i][P.my_num()].x_0;
            auto x_1 = shuffle_matrix[i][P.my_num()].x_1;
            for (size_t q = 0; q < input_size; q++) {           
                SemiShare<open_t<T>> temp_share(x_0[q]);
                SemiShare<open_t<T>> temp_mac(x_1[q]);
                
                T new_ltos_share(x_0[q], x_1[q]);
                w[q] = to_shuffle[q] - new_ltos_share;
            }
            
            octetStream send;
            for (size_t q = 0; q < input_size; q++) {
                w[q].pack(send);
            }
            P.send_to(i, send);

            //Define shares for next round (Step iii in the paper)
            auto y_0 = shuffle_matrix[i][P.my_num()].y_0;
            auto y_1 = shuffle_matrix[i][P.my_num()].y_1;
            for (size_t q = 0; q < input_size; q++) {           
                SemiShare<open_t<T>> temp_share(y_0[q]);
                SemiShare<open_t<T>> temp_mac(y_1[q]);
                
                T new_ltos_share(y_0[q], y_1[q]);
                to_shuffle[q] = new_ltos_share;
            }
        }
    }

    auto end1 = chrono::high_resolution_clock::now();
    if (!verify_permutation(to_shuffle, old, proc, input_size)) {
        throw runtime_error("Permutation verification failed");
    }
    auto end2 = chrono::high_resolution_clock::now();

    auto duration0 = chrono::duration_cast<chrono::microseconds>(start1 - start);

    auto duration1 = chrono::duration_cast<chrono::microseconds>(end1 - start1);
    auto duration2 = chrono::duration_cast<chrono::microseconds>(end2 - start1);
    println_for_party(proc, "LTOS_size_dependent_prep: n=" + to_string(n) + " m=2^" + to_string(mylog2(input_size)) + ": " + to_string(duration0.count()));
    println_for_party(proc, "LTOS_without_verification: n=" + to_string(n) + " m=2^" + to_string(mylog2(input_size)) + ": " + to_string(duration1.count()));
    println_for_party(proc, "LTOS_with_verification: n=" + to_string(n) + " m=2^" + to_string(mylog2(input_size)) + ": " + to_string(duration2.count()));

    for (size_t i = 0; i < n_shuffles; i++) {
        size_t destination = destinations[i];
        //size_t unit_size = unit_sizes[i];
        size_t size = sizes[i];

        for (size_t j = 0; j < size; j++) {
            a[destination + j] = to_shuffle[j];
        }
    }
}



template<class T>
bool verify_permutation(vector<T> &to_check, vector<T> &a, SubProcessor<T>& proc, size_t input_size) {
    auto &P = proc.P;
    size_t me = P.my_num();
    auto &MC = proc.MC;
    auto &prep = proc.DataF;

    T r = prep.get_random(); //There is also a method called get random for open, but we could not find any documentation as to the difference
    T r_prime = prep.get_random();

    MC.init_open(P);
    MC.prepare_open(r);
    MC.exchange(P);
    open_t<T> r_open = MC.finalize_open();
    
    T r_open_const = T::constant(r_open, me, MC.get_alphai());

    MC.Check(P);

    vector<T> first_prod_elements(input_size);
    for (size_t i = 0; i < input_size; i++) {
        first_prod_elements[i] = r_open_const - to_check[i];
    }

    //using that a is not modified yet
    vector<T> second_prod_elements(input_size);
    for (size_t i = 0; i < input_size; i++) {
        second_prod_elements[i] = r_open_const - a[i];
    }
    vector<vector<T>> to_compute = {first_prod_elements, second_prod_elements};
    vector<T> products_before_split = products(to_compute, proc);
    T first_prod = products_before_split[0];
    T second_prod = products_before_split[1];
    T products = first_prod - second_prod;
    
    auto &protocol = proc.protocol;
    protocol.init_mul();
    protocol.prepare_mul(r_prime, products);
    protocol.exchange();
    T result = protocol.finalize_mul();

    MC.init_open(P);
    MC.prepare_open(result);
    MC.exchange(P);
    open_t<T> result_open = MC.finalize_open();
    
    MC.Check(P);
    bool isZero = (typename T::clear(result_open) == 0);

    return isZero;
}

//ASSUMES THAT ALL VECTORS ARE THE SAME SIZE
template<class T>
vector<T> products(vector<vector<T>> &vecs, SubProcessor<T>& proc) {
    auto n = vecs[0].size();
    if (n < 2) {
        vector<T> result(vecs.size());
        for (size_t i = 0; i < vecs.size(); i++) {
            result[i] = vecs[i][0];
        }
        return result;
    }

    auto &protocol = proc.protocol;
    protocol.init_mul();

    for (size_t p = 0; p < vecs.size(); p++) {
        for (size_t i = 0; i < n / 2; i++) {
            protocol.prepare_mul(vecs[p][2*i], vecs[p][2*i+1]);
        }
    }

    protocol.exchange();
    
    for (size_t p = 0; p < vecs.size(); p++) {
        for (size_t i = 0; i < n / 2; i++) {
            vecs[p][i] = protocol.finalize_mul();
        }
    }

    if (n % 2 == 1) {
        for (size_t p = 0; p < vecs.size(); p++) {
            vecs[p][n / 2] = vecs[p][n - 1];
        }
    }

    for (size_t p = 0; p < vecs.size(); p++) {
        vecs[p].resize((n + 1) / 2);
    }

    return products(vecs, proc);
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
vector<int> SecureShuffle<T>::generate_random_permutation(int n) { 
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

/*
    Functions below not in use.
*/
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