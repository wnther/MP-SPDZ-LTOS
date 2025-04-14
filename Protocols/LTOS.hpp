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

// template<class T>
// PermutationMap<T> generate_random_permutation_map(SubProcessor<T>& proc, int vector_length) {
//     vector<int> original(vector_length);
//     iota(original.begin(), original.end(), 0);

//     unsigned seed = chrono::system_clock::now().time_since_epoch().count() + proc.P.my_num();
//     shuffle(original.begin(), original.end(), default_random_engine(seed));

//     map<int, int> perm_map;
//     for (int i = 0; i < vector_length; ++i) {
//         perm_map[i] = original[i];
//     }

//     return perm_map;
// }

template <typename T>
ShuffleVec<T> conduct_preprocessing(SubProcessor<T>& proc, size_t input_size, vector<int> perm_map) {
    
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
        
        // auto st = get_party_stream(proc);
        // st << "prime: " << shuffle_prep.x_0[0].pr() << "\n";
        // Generate z based on the permutation
        for (size_t i = 0; i < input_size; i++) {
            // st << "index for party " << me << " with " << j << perm_map.at(me).at(i+1) << "\n";
            shuffle_prep.z_0[i] = shuffle_prep.x_0[perm_map.at(i)] - shuffle_prep.y_0[i];
            shuffle_prep.z_1[i] = shuffle_prep.x_1[perm_map.at(i)] - shuffle_prep.y_1[i];
        }

        // auto st = get_party_stream(proc);
        // auto rand_map = generate_random_permutation_map(proc, input_size);

        // for (auto& [k, v] : rand_map) {
        //     st << k << " -> " << v << "\n";
        // }

        // st << "Party " << me << " generated x,y,z for party " << j << "\n";
        // for (size_t i = 0; i < input_size; i++) {
        //     st << "x_0, y_0, z_0: " << shuffle_prep.x_0[i] << ", " << shuffle_prep.y_0[i] << ", "<< shuffle_prep.z_0[i] << "\n";
        // }
        // for (size_t i = 0; i < input_size; i++) {
        //     st << "x_1, y_1, z_1: " << shuffle_prep.x_1[i] << ", " << shuffle_prep.y_1[i] << ", "<< shuffle_prep.z_1[i] << "\n";
        // }
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
    

    size_t input_size = sizes[0];

    // clearprint_for_party(proc);
    // println_for_party(proc, "--------------------");
    // auto prime = T::open_type::pr();
    // get_party_stream(proc) << "Prime: " << prime << endl;
    
    vector<int> perm_map = generate_random_permutation(input_size);

    // Preprocessing (Offline)
    ShuffleVec<T> shuffle_matrix = conduct_preprocessing(proc, input_size, perm_map);

    // Main part of the protocol (Online)
    auto &P = proc.P;
    size_t n = P.num_players();
    //auto &input = proc.input;
    size_t me = P.my_num();

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
                rs[me][q] = a[perm_map.at(q)];
            }
            
            // Define shares for next round (Step c in the paper)

            for (size_t q = 0; q < input_size; q++) {
                a[q] = rs[0][q];
                for (size_t j = 1; j < n; j++) {
                    a[q] += rs[j][q];
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

                w[q] = a[q] - new_ltos_share;
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

                a[q] = new_ltos_share;
            }
        }
    }

    if (!verify_permutation(a, proc, input_size)) {
        throw runtime_error("Permutation verification failed");
    }
}



template<class T>
bool verify_permutation(StackedVector<T> &a, SubProcessor<T>& proc, size_t input_size) {

    (void) a;
    (void) input_size;
    (void) proc;

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

    cout << "r_open: " << r_open << endl;
    MC.Check(P);

    vector<T> first_prod_elements(input_size);
    for (size_t i = 0; i < input_size; i++) {
        first_prod_elements[i] = r_open_const - a[i];
    }
    //We assume that the second half of a is equal to the input
    vector<T> second_prod_elements(input_size);
    for (size_t i = 0; i < input_size; i++) {
        second_prod_elements[i] = r_open_const - a[i+input_size];
    }
    T first_prod = product(first_prod_elements, proc);
    T second_prod = product(second_prod_elements, proc);
    T products = first_prod - second_prod;
    vector<T> products2{r_prime, products};
    T result = product(products2, proc);

    MC.init_open(P);
    MC.prepare_open(result);
    MC.exchange(P);
    open_t<T> result_open = MC.finalize_open();
    
    cout << "result_open: " << result_open << endl;

    MC.Check(P);

    // Check if the result is zero

    // result_open.get_share().is_zero();

    // T isZero = (result_open);

    return true;
}

template<class T>
T product(vector<T> &vec, SubProcessor<T>& proc) {
    auto n = vec.size();
    cout << "Product: " << n << endl;
    if (n < 2) {
        return vec[0];
    }
    auto &protocol = proc.protocol;
    protocol.init_mul();
    for (size_t i = 0; i < n / 2; i++) {
        protocol.prepare_mul(vec[2*i], vec[2*i+1]);
    }
    protocol.exchange();
    for (size_t i = 0; i < n / 2; i++) {
        vec[i] = protocol.finalize_mul();
    }
    if (n % 2 == 1) {
        vec[n / 2] = vec[n - 1];
    }
    vec.resize((n + 1) / 2);
    return product(vec, proc);
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