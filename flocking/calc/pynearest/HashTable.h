#ifndef _HASHTABLE_H
#define _HASHTABLE_H
#include "NeighborList.h"
#include "PointSet.h"
#include <list>
template<int d>
class HashTable
{
 public:
  HashTable(const PointSet<d> & pointset, int start, int end);
  void getTableNeighbors(int i, NeighborList & neighborlist) const;
  void refineNearestNeighbors(int i, NeighborList & neighborlist,
			      bool testIfAlreadyTaken = true) const;
  /*  void print()
  {
    for (int i = 0; i < size_; i ++) {
      std::cout << i << ':';
      PointList::const_iterator it;
      for (it = table_[i].begin(); it != table_[i].end(); ++it)
	std::cout << *it << ' ';
      std::cout << std::endl;
    }
    } DEBUG */
 protected:
  int getIndex(int i) const {
    return int((pointset_.getSum(i) - minsum_) * key_);
  }
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
