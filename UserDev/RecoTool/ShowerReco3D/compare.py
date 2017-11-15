import sys,os

fold = open("showers0624.txt",'r')
fnew = open("showers0625.txt",'r')

old_v = []
new_v = []

for line in fold:
    idx_v = line.split(",")[:-1]
    for n in idx_v:
        old_v.append(int(n))

for line in fnew:
    idx_v = line.split(",")[:-1]
    for n in idx_v:
        new_v.append(int(n))

removed_v = []

for idx in old_v:

    found = False

    for ii in new_v:

        if (ii == idx):
            found = True
            break

    if (found == False):
        removed_v.append(idx)
        

created_v = []

for idx in new_v:

    found = False

    for ii in old_v:

        if (ii == idx):
            found = True
            break

    if (found == False):
        created_v.append(idx)

print 'Created showers : '
print
print created_v
print
print
print 'Removed showers : '
print
print removed_v
