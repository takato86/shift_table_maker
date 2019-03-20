

class Staff(object):
    def __init__(self, id, name, name_kanji, charge):
        self.id = id
        self.name = name
        self.name_kanji = name_kanji
        self.charge = charge
        self.n_early_works = 0
        self.n_late_works = 0
    
    def __eq__(self, other):
        if other.id == self.id:
            return True
        else:
            return False

    def early_work(self):
        self.n_early_works += 1
        
    def late_work(self):
        self.n_late_works += 1
    
    def get_total_works(self):
        return self.n_early_works + self.n_late_works
    
    def get_n_early_works(self):
        return self.n_early_works

    def get_n_late_works(self):
        return self.n_late_works
    def get_charge(self):
        return self.charge
    
    def export(self):
        return [self.id, self.name, self.charge, self.n_early_works, self.n_late_works, self.n_early_works+self.n_late_works]
        
