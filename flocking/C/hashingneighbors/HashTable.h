#ifndef _FLOCK_HASHTABLE_H
#define _FLOCK_HASHTABLE_H
#include "NeighborList.h"
#include "PointSet.h"
#include <list>

/**
   HashTable - an HashTable to store points according to the second model of
   storage in M. Vanco and G. Brunnett and Th. Schreiber,
   A Hashing Strategy for Efficient k -Nearest Neighbors Computation, 1999
*/

template<int d>
class HashTable
{
 public:
  typedef double Point[d];
 public:
  /**
     A HashTable is constructed from a subset of a PointSet. The subset
     is determined by the interval [start, end)
  */
  HashTable(const PointSet<d> & pointset, int start, int end);
  /**
     Determine an upper bound on the distance of the k-th neighbor
  */
  double getKthNeighborDistanceSquaredUpperBound(const Point& pt, int k) const;
  /**
     Using an existing, empty, partially filled or filled
     NeighborList, check if there are better candidates in the
     current HashTable to replace some of them.
  */
  void refineNearestNeighbors(const Point& pt,
			      NeighborList & neighborlist,
			      double distance_squared_upper_bound) const;
 protected:
  /**
     Return the index of a point in the current HashTable. If the point
     is out-of-limit, return the nearest bucket (0 or size_ - 1).

     \param pt Point to hash

     \return Index in HashTable
  */
  int getIndex(const Point& pt) const {
    int index = (PointSet<d>::getSum(pt) - minsum_) * key_;
    return std::min(std::max(index, 0), size_ - 1);
  }
  /**
     Update the maximal distance to a given Point pt using elements
     from a hash bucket. Process elements in the hash bucket until
     the number of processed elements number == k or the bucket in
     empty.
  */
  void processDistanceFromBucket(const Point& pt, int bucket,
				 int& number, double& max_distance,
				 int k) const;
  
  const PointSet<d> & pointset_;
  int size_;
  int start_;
  int end_;
  double minsum_;
  double maxsum_;
  double key_;
  typedef std::list<int> PointList;
  std::vector<PointList> table_;
};

#include "HashTable.cpp"
#endif
