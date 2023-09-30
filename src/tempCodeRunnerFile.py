import time

# Record the start time
start_time = time.time()

#lekser(ulaz)
ast = P(ulaz)
ast.izvrši()

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Execution time: {elapsed_time:.6f} seconds")