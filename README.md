# popTextureDS
Generating synthetic popTextures

# User instructions

  >> git clone https://github.com/prashanthtr/popTextureDS.git

  >> cd popTextureDS/

  >> conda create -n popTextureDS python=3.8 ipykernel

  >> conda activate popTextureDS

  >> python3 -m pip install -r requirements.txt --src '.'(please run twice - due to numba dependency error)

# Setup and run jupyter notebook

>> pip install jupyter

>> python3 -m ipykernel install --user --name popTextureDS

>> jupyter notebook

>> Select *popTexture-notebook.ipynb* in the browser interface

# Generate files from commandline

>> python3 generate.py config_file.json
