#ifndef _NEIGHBORLIST_H
#define _NEIGHBORLIST_H
#include <utility>
#include <list>
#include <iostream>
#include <stdexcept>

typedef std::pair<double, int> Neighbor;

class NeighborList
{
 protected:
  typedef std::list<Neighbor> List;
 public:
  typedef List::const_iterator const_iterator;
  NeighborList(int desired_size) : size_(0), desired_size_(desired_size) { }
  void changeToRealOrder(const std::vector<int> & permutation_table)
  {
    List::iterator it;
    for (it = list_.begin(); it != list_.end(); ++it)
      it->second = permutation_table[it->second];
  }
  void clear()
  {
    size_ = 0;
    list_.clear();
  }
  std::list<Neighbor>::const_iterator begin() const
  {
    return list_.begin();
  }
  std::list<Neighbor>::const_iterator end() const
  {
    return list_.end();
  }
  std::list<Neighbor>::const_reference front() const
  {
    return list_.front();
  }
  std::list<Neighbor>::const_reference back() const
  {
    return list_.back();
  }
  int size() const
  {
    return size_;
  }
  bool hasDesiredSize() const
  {
    return size_ == desired_size_;
  }
  bool contains(int i) const
  {
    List::const_iterator it;
    for (it = list_.begin(); it != list_.end(); ++it)
      if (it->second == i)
	return true;
    return false;
  }
  void addNeighbor(const Neighbor& neighbor)
  {/*
    std::cout << "Before :" << std::endl;
    List::iterator it = list_.begin();
    for(;it != list_.end(); ++it)
      std::cout << it->first << " ";
      std::cout << std::endl;*/
    List::iterator place;
    place = std::upper_bound(list_.begin(), list_.end(), neighbor);
    list_.insert(place, neighbor);
    size_ ++;
    /*    std::cout << "After :" << std::endl;
    it = list_.begin();
    for(;it != list_.end(); ++it)
      std::cout << it->first << " ";
      std::cout << std::endl;*/
  }
  void removeFarthestNeighbor()
  {
    if (list_.empty())
      throw std::out_of_range("List is empty");
    list_.pop_back();
    size_ --;
  }
  void addNeighborAndTrim(const Neighbor& neigbhor)
  {
    addNeighbor(neigbhor);
    trim();
  }
  void trim()
  {
    while (size_ > desired_size_)
      removeFarthestNeighbor();
  }
 protected:
  List list_;
  int size_;
  int desired_size_;
};

#endif
