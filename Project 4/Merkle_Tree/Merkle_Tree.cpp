#include "Merkle_Tree.h"
#include <cmath>
#include <algorithm>
#include <functional>

MerkleTree::MerkleTree() : root(nullptr), block_count(0), levels(0) {}

std::string MerkleTree::compute_sm3_hash(const std::string& input) const {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_sm3(), nullptr);
    EVP_DigestUpdate(ctx, input.c_str(), input.size());
    
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    EVP_DigestFinal_ex(ctx, hash, &hash_len);
    EVP_MD_CTX_free(ctx);
    
    std::stringstream ss;
    for (unsigned int i = 0; i < hash_len; i++) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}

MerkleTree::NodePtr MerkleTree::create_node(const std::string& data, const std::string& hash_value, int id) const {
    return std::make_shared<Node>(data, hash_value, id);
}

MerkleTree::NodePtr MerkleTree::merge_nodes(NodePtr left_child, NodePtr right_child) const {
    std::string combined_hash = compute_sm3_hash(left_child->hash_value + right_child->hash_value);
    auto parent_node = create_node("", combined_hash, -1);
    
    parent_node->left = left_child;
    parent_node->right = right_child;
    left_child->parent = parent_node;
    right_child->parent = parent_node;
    
    return parent_node;
}

bool MerkleTree::build_tree(const std::vector<std::string>& data_blocks) {
    if (data_blocks.empty()) {
        return false;
    }
    
    std::vector<NodePtr> current_level;
    block_count = 0;
    
    for (const auto& data : data_blocks) {
        std::string hash = compute_sm3_hash(data);
        auto leaf_node = create_node(data, hash, block_count++);
        current_level.push_back(leaf_node);
    }
    
    levels = static_cast<int>(std::ceil(std::log2(block_count)));
    
    while (current_level.size() > 1) {
        std::vector<NodePtr> next_level;
        
        for (size_t i = 0; i < current_level.size(); i += 2) {
            NodePtr left = current_level[i];
            NodePtr right;
            
            if (i + 1 < current_level.size()) {
                right = current_level[i + 1];
            } else {
                right = create_node("", "", -1);
            }
            
            auto parent = merge_nodes(left, right);
            next_level.push_back(parent);
        }
        
        current_level = std::move(next_level);
    }
    
    root = current_level[0];
    return true;
}

bool MerkleTree::insert_block(const std::string& data) {
    if (data.empty()) {
        std::cout << "Error: Empty block data!" << std::endl;
        return false;
    }
    
    std::vector<std::string> all_data;
    
    std::function<void(NodePtr)> collect_leaf_data = [&](NodePtr node) {
        if (!node) return;
        if (!node->left && !node->right && node->id != -1) {
            all_data.push_back(node->data);
        }
        collect_leaf_data(node->left);
        collect_leaf_data(node->right);
    };
    
    if (root) {
        collect_leaf_data(root);
    }
    all_data.push_back(data);
    
    return build_tree(all_data);
}

std::string MerkleTree::get_root_hash() const {
    return root ? root->hash_value : "";
}

std::string MerkleTree::generate_proof(int block_index) const {
    if (block_index >= block_count || block_index < 0) {
        return "Error: Block index out of range!";
    }
    
    std::vector<NodePtr> leaf_nodes;
    std::function<void(NodePtr)> collect_leaves = [&](NodePtr node) {
        if (!node) return;
        if (!node->left && !node->right && node->id != -1) {
            leaf_nodes.push_back(node);
        }
        collect_leaves(node->left);
        collect_leaves(node->right);
    };
    
    collect_leaves(root);
    
    if (block_index >= static_cast<int>(leaf_nodes.size())) {
        return "Error: Block index out of range!";
    }
    
    std::sort(leaf_nodes.begin(), leaf_nodes.end(), 
              [](const NodePtr& a, const NodePtr& b) { return a->id < b->id; });
    
    NodePtr target_leaf = leaf_nodes[block_index];
    std::vector<std::string> proof_path;
    
    std::function<bool(NodePtr, NodePtr)> find_path = 
        [&](NodePtr current, NodePtr target) -> bool {
        if (!current) return false;
        if (current == target) return true;
        
        if (find_path(current->left, target)) {
            if (current->right) {
                proof_path.push_back("R:" + current->right->hash_value);
            }
            return true;
        }
        
        if (find_path(current->right, target)) {
            if (current->left) {
                proof_path.push_back("L:" + current->left->hash_value);
            }
            return true;
        }
        
        return false;
    };
    
    find_path(root, target_leaf);
    
    std::string proof;
    for (const auto& step : proof_path) {
        proof += step + "\n";
    }
    
    return proof;
}

bool MerkleTree::verify_proof(const std::string& data, const std::string& proof, const std::string& root_hash) const {
    std::string current_hash = compute_sm3_hash(data);
    std::istringstream iss(proof);
    std::string line;
    
    while (std::getline(iss, line)) {
        if (line.length() < 3) continue;
        
        char direction = line[0];
        std::string sibling_hash = line.substr(2);
        
        if (direction == 'L') {
            current_hash = compute_sm3_hash(sibling_hash + current_hash);
        } else if (direction == 'R') {
            current_hash = compute_sm3_hash(current_hash + sibling_hash);
        }
    }
    
    return current_hash == root_hash;
}

int main() {
    MerkleTree tree;
    
    std::vector<std::string> initial_data = {
        "84", "75", "41", "74", "42", "0", "16", "83", "63", "94",
        "80", "15", "90", "47", "39", "61", "21", "62", "99", "38"
    };
    
    if (tree.build_tree(initial_data)) {
        std::cout << "Successfully constructed Merkle tree with " << initial_data.size() << " blocks" << std::endl;
        std::cout << "Root hash: " << tree.get_root_hash() << std::endl;
    }
    
    std::string root_before_insert = tree.get_root_hash();
    
    if (tree.insert_block("sdu-ljm")) {
        std::cout << "Successfully inserted new block 'sdu-ljm'" << std::endl;
        std::cout << "New root hash: " << tree.get_root_hash() << std::endl;
    }
    
    std::string proof = tree.generate_proof(4);
    if (!proof.empty() && proof.find("Error") == std::string::npos) {
        std::cout << "\nProof of inclusion for block 4 (data: '42'):" << std::endl;
        std::cout << proof << std::endl;
        
        bool is_valid = tree.verify_proof("42", proof, tree.get_root_hash());
        std::cout << "Proof verification: " << (is_valid ? "VALID" : "INVALID") << std::endl;
    }
    
    return 0;
}