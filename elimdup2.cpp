/* Eliminate duplicated entries from an edge list file                */
/* Compile by g++ -O3 elimdup2.cpp -o elimdup */
/* Run by: elimdup -i infile -o outfile */
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <numeric>

int main(int argc, char *argv[]) {
  std::ifstream edgelist;
  std::ofstream outfile;
  for (int i=1; i<argc; i++) {
    if ((std::string) argv[i] == "-i") edgelist.open(argv[i+1]); /* Input file */
    if ((std::string) argv[i] == "-o") outfile.open(argv[i+1]); /* Output file */
  }
  int n = 0, e = 0;
  std::vector<std::vector<int> > edges;
  std::map<int, int> n_map;
  std::string line;
  while (std::getline(edgelist,line)) {
    int i, j;
    std::istringstream iss(line);
    if (line[0] != '#' && (iss >> i >> j)) {
      if (n_map.count(i) == 0) {
        edges.push_back({});
        n_map.insert(std::pair<int,int>(i, n++));
      }
      if (n_map.count(j) == 0) {
        edges.push_back({});
        n_map.insert(std::pair<int,int>(j, n++));
      }
      edges[n_map[i]].push_back(n_map[j]);
      edges[n_map[j]].push_back(n_map[i]);
      e++;
    }
  }
  edgelist.close();
  std::cout << "No. nodes: " << n << ", No. edges: " << e << std::endl;
  outfile << "# No. nodes: " << n << ", No. edges: " << e << std::endl;
  for (std::vector<std::vector<int> >::iterator lk=edges.begin(); lk!=edges.end(); ++lk) {
    int temp = 0, i = lk - edges.begin();
    std::sort (lk->begin(), lk->end());
    for (std::vector<int>::iterator it=lk->begin(); it!=lk->end(); ++it) if (*it > i && *it > temp) {
      outfile << i << '\t' << *it << std::endl;
      temp = *it;
    }
  }
  outfile.close();
  return 0;
}
