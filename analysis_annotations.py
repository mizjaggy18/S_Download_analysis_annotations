# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2018. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.


__author__ = "WSH Munirah W Ahmad <wshmunirah@gmail.com>"
__copyright__ = "Apache 2 license. Made by Multimedia University Cytomine Team, Cyberjaya, Malaysia, http://cytomine.mmu.edu.my/"
__version__ = "1.0.0"

import os
import logging
import sys
import shutil

import cytomine
from cytomine.models import Property, Annotation, AnnotationTerm, AnnotationCollection, JobData, Job, TermCollection


# Date created: 14 December 2021

def run(cyto_job, parameters):
    logging.info("----- test software v%s -----", __version__)
    logging.info("Entering run(cyto_job=%s, parameters=%s)", cyto_job, parameters)

    job = cyto_job.job
    project = cyto_job.project

    # I create a working directory that I will delete at the end of this run
    working_path = os.path.join("tmp", str(job.id))
    if not os.path.exists(working_path):
        logging.info("Creating working directory: %s", working_path)
        os.makedirs(working_path)
    try:
        
        id_project=project.id
        # id_image = parameters.cytomine_id_images
        id_job=parameters.cytomine_id_job
        id_user = parameters.cytomine_id_user
        # download_path = conn.parameters.download_path
        download_size = parameters.download_size

        annotations = AnnotationCollection()        
        annotations.project = id_project
        annotations.job = id_job
        annotations.user = id_user
        annotations.showAlgo = True
        annotations.showWKT = True
        annotations.showMeta = True
        annotations.showGIS = True
        annotations.showTerm = True
        annotations.annotation = True
        annotations.fetch()
        print(annotations)

        nb_annotations=len(annotations)
        logging.info("# annotations in this job and project: %d", nb_annotations)

        progress = 0
        progress_delta = 100 / nb_annotations

        output_path = os.path.join(working_path, "annotations.csv")
        f= open(output_path,"w+")
        f.write("ID;Image;Project;JobID;Term;User;Area;Perimeter;WKT \n")

        for annotation in annotations:
            job.update(progress=progress, statusComment="Analyzing annotation {}...".format(annotation.id))
            progress += progress_delta
            f.write("{};{};{};{};{};{};{};{}\n".format(annotation.id,annotation.image,annotation.project,annotation.term,annotation.user,annotation.area,annotation.perimeter,annotation.location))
            #f.write("{};{};{};{};{};{};{};{};{}\n".format(annotation.id,annotation.image,annotation.project,annotation.job,annotation.term,annotation.user,annotation.area,annotation.perimeter,annotation.location))
        f.close()   
        
        #I save a file generated by this run into a "job data" that will be available in the UI. 
        job_data = JobData(job.id, "Generated File", "annotations.csv").save()
        job_data.upload(output_path)

    finally:
        logging.info("Deleting folder %s", working_path)
        shutil.rmtree(working_path, ignore_errors=True)
        logging.debug("Leaving run()")


if __name__ == "__main__":
    logging.debug("Command: %s", sys.argv)

    with cytomine.CytomineJob.from_cli(sys.argv) as cyto_job:
        run(cyto_job, cyto_job.parameters)


