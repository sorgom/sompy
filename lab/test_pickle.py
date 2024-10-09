import pickle

dfile = 'data.pkl'

# Create a dictionary object
data1 = { 'a': 1, 'b': { 1, 2, 3}, 'c': [1, 2, 3] }
print(data1)

with open(dfile, 'wb') as fh:
    # Store the data
    pickle.dump(data1, fh)

with open(dfile, 'rb') as fh:
    # Load the data
    data2 = pickle.load(fh)
    print(data2)
    print(data2 == data1)
