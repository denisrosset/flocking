#include "../PointSet.h"
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
  if (neighborlist.size() != k)
    throw logic_error("Not enough results");
  for (int i = 0; i < k; i++) {
    if (it->second != referencelist[i].second) {
      NeighborList::const_iterator it1 = neighborlist.begin();
      std::cout << "Optimized list :" << std::endl;
      for (;it1 != neighborlist.end(); ++it1)
	std::cout << it1->second << " " << it1->first << std::endl;
      std::cout << std::endl;
      std::cout << "Naive list :" << std::endl;
      for (int j = 0; j < k; j ++)
	std::cout << referencelist[j].second << " " << referencelist[j].first << std::endl;
      std::cout << std::endl;
      throw logic_error("Lists not equal");
    }
    ++it;
  }
  //  std::cout << "." << std::flush;
}

const int reps = 100;
const int N = 10001;
const int d = 2;
const int m = 12;
const int k = 8;
const int r = 4;
const double L = 1;

void test_flat_world()
{
  for (int rep = 0; rep < reps; rep ++) {
    double points[N][d];
    double pt[d];
    for (int j = 0; j < d; j++) {
      for (int i = 0; i < N; i++)
	points[i][j] = ((double)std::rand())/RAND_MAX;
      pt[j] = ((double)std::rand())/RAND_MAX;
    }
    vector<pair<double, int> > list_points;
    for (int i = 0; i < N; i++) {
      double distance_sq = 0;
      for (int a = 0; a < d; a++)
	distance_sq += (pt[a] - points[i][a]) * (pt[a] - points[i][a]);
      list_points.push_back(pair<double, int>(distance_sq, i));
    }		    
    sort(list_points.begin(), list_points.end());
    
    PointSet<d> pointset(points, N, m, r);
    NeighborList * neighborlist;
    
    // Direct addition to neighbor list
    neighborlist = new NeighborList(k);
    for (int i = 0; i < N; i++)
      neighborlist->addNeighborAndTrim(pointset.createNeighbor(pt, i));
    neighborlist->sortFinalResults();
    assert_equal_lists(*neighborlist, list_points, k);
    delete neighborlist;
    
    // Giant hashtable for entire pointset
    HashTable<d> h = HashTable<d>(pointset, 0, N);
    double distance_sq_ub = h.getKthNeighborDistanceSquaredUpperBound(pt, k);
    neighborlist = new NeighborList(k);
    h.refineNearestNeighbors(pt, *neighborlist, distance_sq_ub);
    neighborlist->sortFinalResults();
    assert_equal_lists(*neighborlist, list_points, k);
    delete neighborlist;
    
    // Complete algorithm
    pointset.init();
    neighborlist = pointset.getNeighborListInRealOrder(pt, k);
    neighborlist->sortFinalResults();
    assert_equal_lists(*neighborlist, list_points, k);
    delete neighborlist;
  }
}

double comp_sub(double a, double b, double L)
{
  double d = a - b;
  d = d < -L/2 ? d + L : d;
  d = d > L/2 ? d - L : d;
  return d;
}

void test_torus_world()
{
  for (int rep = 0; rep < reps; rep ++) {
    double points[N][d];
    double pt[d];
    for (int j = 0; j < d; j++) {
      for (int i = 0; i < N; i++)
	points[i][j] = ((double)std::rand())/RAND_MAX;
      pt[j] = ((double)std::rand())/RAND_MAX;
    }
    vector<pair<double, int> > list_points;
    for (int i = 0; i < N; i++) {
      double distance_sq = 0;
      for (int a = 0; a < d; a++)
	distance_sq += comp_sub(pt[a], points[i][a], L) * 
	  comp_sub(pt[a], points[i][a], L);
      list_points.push_back(pair<double, int>(distance_sq, i));
    }			    
    sort(list_points.begin(), list_points.end());

    PointSet<d> pointset(points, N, m, r);
    NeighborList * neighborlist;
    pointset.init();
    neighborlist = pointset.getWrapNeighborListInRealOrder(pt, k, L);
    neighborlist->sortFinalResults();
    assert_equal_lists(*neighborlist, list_points, k);
    delete neighborlist;
    for (int pp = 0; pp < N; pp++) {
      pointset.copyPoint(pt, points[pp]);
      neighborlist = pointset.getWrapNeighborListInRealOrder(pt, k, L);
      neighborlist->sortFinalResults();
      delete neighborlist;
    }
  }
}


int main()
{
  test_flat_world();
  test_torus_world();
}
