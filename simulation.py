"""
This script is for simulating data for the purpose of training a GAN.
The method is to use the isolation with migration scenario from the pg-gan simulation software.
The msprime module is used to perform the simulation and the tskit module is used to generate haplotype data.
"""

# Import relevant libraries
import os
import msprime
import numpy as np

# Function for simulating data
def im(params, sample_sizes, seed, reco):
    """Simulate data for 2 populations."""
    assert len(sample_sizes) == 2

    # Extract parameters
    N1 = params.get("N1")
    N2 = params.get("N2")
    T_split = params.get("T_split")
    N_anc = params.get("N_anc")

    # Define population configurations
    population_configurations = [
        msprime.PopulationConfiguration(sample_size=sample_sizes[0], initial_size=N1),
        msprime.PopulationConfiguration(sample_size=sample_sizes[1], initial_size=N2)
    ]

    # Define migration events
    mig = params.get("mig")
    mig_time = T_split / 2  # no migration initially
    if mig >= 0:  # directional (pulse)
        mig_event = msprime.MassMigration(time=mig_time, source=1, destination=0, proportion=abs(mig))  # migration from pop 1 into pop 0 (back in time)
    else:
        mig_event = msprime.MassMigration(time=mig_time, source=0, destination=1, proportion=abs(mig))  # migration from pop 0 into pop 1 (back in time)

    # Define demographic events
    demographic_events = [
        mig_event,
        msprime.MassMigration(time=T_split, source=1, destination=0, proportion=1.0),  # move all in deme 1 to deme 0
        msprime.PopulationParametersChange(time=T_split, initial_size=N_anc, population_id=0)  # change to ancestral size
    ]

    # Simulate tree sequence
    ts = msprime.simulate(
        population_configurations=population_configurations,
        demographic_events=demographic_events,
        mutation_rate=params.get("mut"),
        length=params.get("length"),
        recombination_rate=reco,
        random_seed=seed
    )

    return ts

# Define parameters
params = {
    "N1": 158124480,    # Population 1 size (158,124,480)
    "N2": 54259530,     # Population 2 size (54,259,530)
    "T_split": 1018,    # Time of population split
    "N_anc": 7148911,   # Ancestral population size (7,148,911)
    "mut": 3.5e-9,      # Mutation rate
    "length": 1e4       # Sequence length
}

sample_sizes = [50, 50]  # Sample sizes for two populations
seed = None              # Random seed
reco = 8.4e-9            # Recombination rate

# Define migration rates
migration_rates = [1e-9, 0.1, 0.9]

# Output directory
output_directory = "/Users/jeremiahmushtaq/Documents/University/MSc Research Project/Simulation Results/Simulation 2"

# Function to save haplotype data
def save_haplotypes(ts, output_file):
    # Generate haplotypes
    haplotypes = ts.genotype_matrix().T  # Transpose to get individuals x variants
    np.savetxt(output_file, haplotypes, fmt='%d', delimiter='\t')

# Perform simulations
for mig_rate in migration_rates:
    params["mig"] = mig_rate
    for i in range(10000):
        ts = im(params, sample_sizes, seed, reco)
        
        # Define the output file name for each haplotype data file
        output_file = os.path.join(output_directory, f"haplotypes_mig{mig_rate}_rep{i+1}.txt")
        
        # Save haplotype data to a file
        save_haplotypes(ts, output_file)