#ifndef _HASHTABLE_H
#define _HASHTABLE_H
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
  /**
     A HashTable is constructed from a subset of a PointSet. The subset
     is determined by the interval [start, end)
  */
  HashTable(const PointSet<d> & pointset, int start, int end);
  /**
     Fill neighborlist with immediate HashTable neighbors of element i.
     They are not the neighbors in the geometric sense, but a mediocre
     approximation.
  */
  void getTableNeighbors(int i, NeighborList & neighborlist) const;
  /**
     Using an already filled NeighborList, check if there are better
     candidates in the current HashTable to replace some of them.
  */
  void refineNearestNeighbors(int i, NeighborList & neighborlist,
			      bool testIfAlreadyTaken = true) const;
 protected:
  int getIndex(int i) const {
    return int((pointset_.getSum(i) - minsum_) * key_);
  }
  /**
     Add elements from the HashTable bucket hash_i in the NeighborList
  neighborlist, until the neighborlist is filled up or we run out of
  elements in the bucket
  */
  void addNeighborsUntilDesiredSize(int i, int hash_i, NeighborList & neighborlist) const;
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
