template<int d>
HashTable<d>::HashTable(const PointSet<d> & pointset, int start, int end)
  : pointset_(pointset), start_(start), end_(end)
{
  size_ = end - start;
  table_.resize(size_);
  for (int i = 0; i < size_; i ++)
    table_[i] = PointList();
  maxsum_ = minsum_ = pointset_.getSum(start);
  for (int i = start + 1; i < end; i ++) {
    double coordsum = pointset_.getSum(i);
    minsum_ = std::min(minsum_, coordsum);
    maxsum_ = std::max(maxsum_, coordsum);
  }
  key_ = (size_ - 1) / (maxsum_ - minsum_);
  for (int i = start; i < end; i ++) {
    int index = getIndex(i);
    table_[index].push_back(i);
  }
}

template<int d>
void 
HashTable<d>::addNeighborsUntilDesiredSize(int i,
					int hash_i,
					NeighborList & neighborlist) const
{
  PointList::const_iterator it;
  for (it = table_[hash_i].begin(); it != table_[hash_i].end(); ++it) {
    if (neighborlist.hasDesiredSize())
      return;
    if (*it != i)
      neighborlist.addNeighbor(pointset_.createNeighbor(i, *it));
  }
}

template<int d>
void
HashTable<d>::getTableNeighbors(int i, NeighborList & neighborlist) const
{
  neighborlist.clear();
  int hash_i = getIndex(i);
  addNeighborsUntilDesiredSize(i, hash_i, neighborlist);
    for (int j = 1; j < size_; j ++) {
      if (neighborlist.hasDesiredSize())
	return;
      if (hash_i + j < table_.size())
	addNeighborsUntilDesiredSize(i, hash_i + j, neighborlist);
      if (hash_i - j >= 0)
	addNeighborsUntilDesiredSize(i, hash_i - j, neighborlist);
    }
}

template<int d>
void
HashTable<d>::refineNearestNeighbors(int i, NeighborList & neighborlist,
				     bool testIfAlreadyTaken) const
{
  double dsquared = neighborlist.back().first;
  double sumpt = pointset_.getSum(i);
  double dimfact = std::sqrt(d * dsquared);
  int start = int(
		  (sumpt - minsum_ - dimfact) * key_);
  int end = int(std::ceil(
			  (sumpt - minsum_ + dimfact) * key_)) + 1;
  start = std::max(start, 0);
  end = std::min(end, size_);
  /*  start = 0;
      end = size_; // DEBUG*/
  for (int j = start; j < end; j++) {
    PointList::const_iterator it;
    for (it = table_[j].begin(); it != table_[j].end(); ++it) {
      double distance_squared = pointset_.getDistanceSquared(i, *it);
      if (distance_squared < neighborlist.back().first and *it != i) {
	if (testIfAlreadyTaken && neighborlist.contains(*it))
	  continue;
	neighborlist.addNeighborAndTrim(pointset_.createNeighbor(i, *it));
      }
    }
  }
}
