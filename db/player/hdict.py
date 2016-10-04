
import unittest

class HierarchicalDict(dict):
    def __init__(self,initialDictionary={}):
        super(HierarchicalDict, self).__init__(initialDictionary)

    def update(self,dict2):

        if dict2 is None:
            dict.update(self,dict2)
        elif not isinstance(dict2, dict):
            dict.update(self,dict2)

        for key in dict2:
            if key in self:
                if isinstance(self[key], dict) and not isinstance(self[key], HierarchicalDict):
                    self[key] = HierarchicalDict(self[key])

                if isinstance(self[key], HierarchicalDict):
                    if isinstance(dict2[key], dict):
                        self[key].update(dict2[key])
                    else:
                        self[key][''] = dict2[key]

                elif not isinstance(self[key], HierarchicalDict) and isinstance(dict2[key], dict):
                    oldKeyValue = self[key]
                    self[key] = HierarchicalDict(dict2[key])
                    if '' not in self[key]:
                        self[key][''] = oldKeyValue

                elif isinstance(self[key], list) or isinstance(dict2[key], list):

                    if not isinstance(self[key], list):
                        self[key] = [ self[key] ]

                    list_to_add = dict2[key]
                    if not isinstance(list_to_add, list):
                        list_to_add = [ list_to_add ]

                    # list contains only unique values
                    self[key] = self[key] + list(set(list_to_add) - set(self[key]))

                else:
                    self[key] = dict2[key]
            else:
                self[key] = dict2[key]


class TestHierarchicalDict(unittest.TestCase):

    def testUpdate(self):

        da = HierarchicalDict({'a':11})
        db = {'b':13}

        da.update(db)
        print da
        self.assertEquals(len(da), 2)
        self.assertEquals(len(db), 1)
        self.assertEquals(da['b'], 13)

        dc = {'c':17, 'b':db}
        da.update(dc)
        self.assertEquals(len(da), 3)
        print da
        self.assertEquals(da['b']['b'], 13)

        dd = {'a':da, 'b':{'b':0}, 'c':dc}
        self.assertEquals(dd['b']['b'],0)
        self.assertEquals(dc['b']['b'],13)

        dc.update(dd)
        self.assertEquals(dc['b']['b'],0)
        print dc

    def testUpdate2(self):

        stat1 = {'foo':{'2015':{'a':'b', 'c':'d', 'e':'f'}}}
        hd = HierarchicalDict(stat1)

        self.assertEquals(hd['foo']['2015']['a'],'b')
        self.assertEquals(len(hd),1)
        self.assertEquals(len(hd['foo']),1)
        self.assertEquals(len(hd['foo']['2015']),3)

        # this next set of updates with {} and stat1 should do absolutely nothing
        hd.update({})
        hd.update(stat1)
        self.assertEquals(hd['foo']['2015']['a'],'b')
        self.assertEquals(len(hd),1)
        self.assertEquals(len(hd['foo']),1)
        self.assertEquals(len(hd['foo']['2015']),3)

        stat2 = {'bar':{'2014':{'x':'y', 'r':'t', 'w':'x'}}}
        hd.update(stat2)
        self.assertEquals(hd['foo']['2015']['a'],'b')
        self.assertEquals(hd['bar']['2014']['x'],'y')
        self.assertEquals(hd['bar']['2014']['w'],'x')
        self.assertEquals(len(hd),2)
        self.assertEquals(len(hd['foo']),1)
        self.assertEquals(len(hd['foo']['2015']),3)

        stat3 = {'foobar':{'2015':{'x':'y', 'r':'t', 'w':'x'}}}
        hd.update(stat3)
        self.assertEquals(hd['foo']['2015']['a'],'b')
        self.assertEquals(hd['bar']['2014']['x'],'y')
        self.assertEquals(hd['bar']['2014']['w'],'x')
        self.assertEquals(hd['foobar']['2015']['x'],'y')
        self.assertEquals(len(hd),3)
        self.assertEquals(len(hd['foo']),1)
        self.assertEquals(len(hd['foo']['2015']),3)

        stat4 = {'foo':{'2014':{'a':'b', 'c':'d', 'e':'f'}}}
        hd.update(stat4)
        self.assertEquals(hd['foo']['2015']['a'],'b')
        self.assertEquals(len(hd),3)
        self.assertEquals(len(hd['foo']),2)
        self.assertEquals(len(hd['foo']['2015']),3)

        stat5 = {'foo':{'2015':{'a':'x', 'c':'z', 'e':'f', 'g':'h'}}}
        hd.update(stat5)
        self.assertEquals(hd['foo']['2015']['a'],'x')
        self.assertEquals(len(hd),3)
        self.assertEquals(len(hd['foo']),2)
        self.assertEquals(len(hd['foo']['2015']),4)
        self.assertEquals(hd['foo']['2015']['c'],'z')
        self.assertEquals(hd['foo']['2015']['e'],'f')
        self.assertEquals(hd['foo']['2015']['g'],'h')

        stat6 = {'foo':'bar'}
        hd.update(stat6)
        self.assertEquals(len(hd),3)
        self.assertEquals(len(hd['foo']),3)
        self.assertEquals(hd['foo'][''],'bar')

        stat7 = {'foo':{'2015':{'a':{'this':'deep'}}}}
        hd.update(stat7)
        self.assertEquals(hd['foo']['2015']['a']['this'],'deep')
        self.assertEquals(hd['foo']['2015']['a'][''],'x')
        self.assertEquals(len(hd['foo']['2015']['a']),2)

    def testUpdateWithList(self):
        hd = HierarchicalDict({})
        hd.update({'a':'1','b':[2]})
        hd.update({'a':['2'],'b':'1'})
        print hd
        self.assertEquals(len(hd['a']),2)
        self.assertEquals(len(hd['b']),2)

if __name__ == '__main__':
    unittest.main()