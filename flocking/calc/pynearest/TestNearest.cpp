#include "PointSet.h"
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <vector>
#include <utility>
#include <iostream>
#include <stdexcept>
using namespace std;
void assert_equal_lists(const NeighborList & neighborlist,
			const vector<pair<double, int> > & referencelist,
			int k)
{
  NeighborList::const_iterator it = neighborlist.begin();
  for (int i = 0; i < k; i++) {
    if (it->second != referencelist[i].second) {
      std::list<Neighbor>::const_iterator it1 = neighborlist.begin();
      for (int j = 0; j < k; j++) {
	std::cout << it1->first << " " << referencelist[j].first << std::endl;
	++it1;
      }
      throw logic_error("Invalid results");
    }
    ++it;
  }
  std::cout << "Passed." << std::endl;
}
int main()
{
  const int N = 10001;
  const int d = 2;
  const int m = 10;
  const int k = 8;
  const int r = 10;
  for (int rep = 0; rep < 1000; rep ++) {
    double points[N][d];
    for (int i = 0; i < N; i++)
      for (int j = 0; j < d; j++)
	points[i][j] = ((double)std::rand())/RAND_MAX;
    PointSet<d> pointset(points, N, m, r);
    vector<pair<double, int> > list_points;
    for (int i = 1; i < N; i++)
      list_points.push_back(pair<double, int>(pointset.getDistanceSquared(0, i), i));
    sort(list_points.begin(), list_points.end());
    NeighborList * neighborlist;

    /*
    std::cout << "Direct addition to neighbor list" << std::endl;
    neighborlist = new NeighborList(k);
    for (int i = 1; i < N; i++)
      neighborlist->addNeighbor(pointset.createNeighbor(0, i));
    assert_equal_lists(*neighborlist, list_points, k);
  
    std::cout << "Giant hashtable for entire pointset" << std::endl;
    HashTable<d> h = HashTable<d>(pointset, 0, N);
    h.getTableNeighbors(0, *neighborlist);
    h.refineNearestNeighbors(0, *neighborlist, true);
    assert_equal_lists(*neighborlist, list_points, k);*/

    std::cout << "Complete algorithm" << std::endl;
    std::cout << "Init" << std::endl;
    pointset.init();
    std::cout << "Query" << std::endl;
    neighborlist = pointset.getNeighborListInRealOrder(0, k);
    assert_equal_lists(*neighborlist, list_points, k);
    delete neighborlist;

    /*  std::list<Neighbor>::const_iterator it = neighborlist->begin();
	for (int i = 0; i < k; i++) {
	std::cout << it->first << " " << list_points[i].first << std::endl;
	++it;
	}*/
  }
}
