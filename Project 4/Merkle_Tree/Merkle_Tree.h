#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <memory>
#include <openssl/evp.h>

class MerkleTree {
public:
    struct Node {
        std::string data;
        std::string hash_value;
        int id;
        std::shared_ptr<Node> left;
        std::shared_ptr<Node> right;
        std::weak_ptr<Node> parent;
        
        Node(const std::string& d = "", const std::string& h = "", int i = -1)
            : data(d), hash_value(h), id(i) {}
    };

    using NodePtr = std::shared_ptr<Node>;

private:
    NodePtr root;
    int block_count;
    int levels;

    std::string compute_sm3_hash(const std::string& input) const;
    NodePtr create_node(const std::string& data, const std::string& hash_value, int id) const;
    NodePtr merge_nodes(NodePtr left_child, NodePtr right_child) const;

public:
    MerkleTree();
    ~MerkleTree() = default;

    bool build_tree(const std::vector<std::string>& data_blocks);
    bool insert_block(const std::string& data);
    std::string get_root_hash() const;
    std::string generate_proof(int block_index) const;
    bool verify_proof(const std::string& data, const std::string& proof, const std::string& root_hash) const;
    
    int get_block_count() const { return block_count; }
    int get_levels() const { return levels; }
};


