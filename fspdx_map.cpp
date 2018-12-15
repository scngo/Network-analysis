/* Import the network and output the strength of the friendship paradox */
/* with both the actual observation and theoretical prediction          */
/* Compile by g++ -O3 fspdx_map.cpp -o fspdx */
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <chrono>
#include <cmath>

int main() {
  auto tstart = std::chrono::system_clock::now();
  std::map<int, std::vector<int> > nn_map;
  std::string line;
  std::ifstream edgelist("./Sets21o5/21o5sn031");
  while (std::getline(edgelist,line)) {
    int i, j;
    std::istringstream iss(line);
    if (line[0] != '#' && (iss >> i >> j)) {
      nn_map[i].push_back(j);
      nn_map[j].push_back(i);
    }
  }
  edgelist.close();
  std::ofstream outfile;
  outfile.open("fspdx.out"); /* Output file */

  int n = nn_map.rbegin()->first + 1;
  std::vector<std::vector<int> > nn_seq(n);
  for (int i=0; i<n; i++) nn_seq[i].swap(nn_map[i]);
  std::vector<int> k(n);
  for (int i=0; i<n; i++) k[i] = nn_seq[i].size();;
  int e = std::accumulate(k.begin(), k.end(), 0)/2;
  int k_max = *std::max_element(k.begin(), k.end());
  std::cout << "No. nodes: " << n << ", No. edges: " << e << ", Max degree: " << k_max << std::endl;

  /* Assortativity */
  double c = 0.0, s = 0.0, avg_q = 0.0;
  std::vector<int> k_hist(k_max+1);
  for (int i=0; i<n; i++) k_hist[k[i]]++;
  std::vector<double> Q(k_max+1);
  for (int i=0; i<k_max+1; i++) Q[i] = (double) i*k_hist[i]/e/2;
  for (int i=0; i<k_max+1; i++) avg_q += i*Q[i];
  for (int i=0; i<k_max+1; i++) s += (i-avg_q)*(i-avg_q)*Q[i];
  for (int i=0; i<n; i++) for (int j=0; j<k[i]; j++) c += (k[i]-avg_q)*(k[nn_seq[i][j]]-avg_q)/e/2;
  double r = c/s;
  std::cout << "Network assortativity: " << r << std::endl;

  for (int i=0; i<n; i++) for (int j=0; j<k[i]; j++) nn_seq[i][j] = k[nn_seq[i][j]];
  std::vector<double> nn_median(n);
  for (int i=0; i<n; i++) {
    std::sort (nn_seq[i].begin(), nn_seq[i].end());
    if (k[i]%2) nn_median[i] = (double) nn_seq[i][(k[i]-1)/2];
    else nn_median[i] = (double) (nn_seq[i][k[i]/2-1] + nn_seq[i][k[i]/2])/2.0;
  }
  std::vector<double> paradox_class(k_max+1);
  for (int i=0; i<n; i++) if (nn_median[i]>k[i]) paradox_class[k[i]]++;

  std::vector<std::vector<double> > P_f(k_max+1, std::vector<double> (2,0));
  for (int i=0; i<n; i++) {
    double ph = 0.0, pl = 0.0;
    for (int j=0; j<k[i]; j++) if (nn_seq[i][j] <= k[i]) pl += 1.0/(double) k[i]; else ph += 1.0/(double) k[i];
    P_f[k[i]][0] += ph / (double) k_hist[k[i]];
    P_f[k[i]][1] += ph * ph / (double) k_hist[k[i]];
  }
  for (int i=0; i<k_max+1; i++) P_f[i][1] = sqrt(P_f[i][1] - P_f[i][0] * P_f[i][0]);

  int paradox = 0;
  for (auto& pc : paradox_class) paradox += pc;
  std::cout << "Paradox: " << paradox << '/' << n << " = " << (double) paradox/n << std::endl;
  for (int i=0; i<k_max+1; i++) if (k_hist[i]) outfile << i << ", " << k_hist[i] << ", " << paradox_class[i] << "; ";
  outfile << '\n' << std::endl;

  std::vector<double> P_maj_class(k_max+1);
  P_maj_class[1] = P_f[1][0];
  for (int i=2; i<k_max+1; i++) if (P_f[i][1] > 0.0 && P_f[i][0] < 1.0 && k_hist[i] != 0) {
    double z = (0.5 - P_f[i][0]) / P_f[i][1];
    //double z = (0.5-P_f[i][0]) / sqrt(P_f[i][0]*(1-P_f[i][0])) * sqrt(i);
    P_maj_class[i] = 0.5 - 0.5 * erf(z/sqrt(2)); /* Normal CDF tail integral */
  }

  double P_maj = 0.0;
  for (int i=0; i<k_max+1; i++) P_maj += (double) k_hist[i]/n * P_maj_class[i];
  std::cout << "Prob of Maj: " << P_maj << std::endl;
  outfile << "Paradox: " << paradox << '/' << n << " = " << (double) paradox/n << std::endl;
  outfile << "Prob of Maj: " <<  P_maj << '\n' << std::endl;
  for (int i=0; i<k_max+1; i++) if (k_hist[i]) outfile << i << ", " << P_maj_class[i] << "; ";
  outfile << '\n' << std::endl;
  for (int i=0; i<k_max+1; i++) if (k_hist[i]) outfile << i << ", " << P_f[i][0] << ", " << P_f[i][1]  << "; ";
  outfile << '\n' << std::endl;

  outfile.close();
  std::chrono::duration<double> elapsed = std::chrono::system_clock::now() - tstart;
  std::cout << "Time used: " <<  elapsed.count() << " sec" << std::endl;
  return 0;
}
