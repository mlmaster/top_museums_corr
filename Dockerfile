FROM jupyter/base-notebook

USER $NB_UID

RUN pip install --upgrade pip && \
    pip install wikipedia && \
    pip install pandas && \
    pip install matplotlib && \
    pip install seaborn && \
    pip install scipy && \
    pip install numpy && \
    pip install html5lib && \
    pip install lxml && \
    fix-permissions "/home/${NB_USER}"

RUN mkdir -p ./top_museums/data/db/
RUN mkdir -p ./top_museums/data/external/dump/

COPY ./README.md ./top_museums/

COPY ./notebooks/top_museums.ipynb ./top_museums/notebooks/

COPY ./data/external/location_density_google.csv ./top_museums/data/external/
COPY ./data/external/worldcities.csv ./top_museums/data/external/

COPY ./data/scripts/__init__.py ./top_museums/data/scripts/
COPY ./data/scripts/generate_db.py ./top_museums/data/scripts/


	