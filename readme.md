* > python -m venv ./env  
* > ./env/Scripts/activate 

== \n
pip install fastapi
fastapi dev app/main.py
== \n
pip freeze > requirements.txt
== \n
vs code add interpreter so that suggestion can be come
Shift+ctrcl+P => interpreter Path => /env/**
== \n
1. build
docker build -t fastapilearn .
2. test
docker run -d --name learncontainer -p 80:80 fastapilearn 

3. create docker repo in artifact registry
gcloud artifacts repositories create quickstart-docker-repo --repository-format=docker \
    --location=us-central1 --description="Docker repository" \
    --project=PROJECT

    gcloud artifacts repositories create fastapilearn --repository-format=docker  --location=asia-south1 --description="Docker repository" --project=dj-ui-dev-e5ba4

-- gcloud artifacts repositories list --project=dj-ui-dev-e5ba4

4. auth config add
gcloud auth configure-docker us-central1-docker.pkg.dev

5. tag
docker tag fastapilearn asia-south1-docker.pkg.dev/dj-ui-dev-e5ba4/fastapilearn/learn-image:tag1

6. push
docker push asia-south1-docker.pkg.dev/dj-ui-dev-e5ba4/fastapilearn/learn-image:tag1 

7. deploy
gcloud run deploy --image=asia-south1-docker.pkg.dev/dj-ui-dev-e5ba4/fastapilearn/learn-image:tag1 --project=dj-ui-dev-e5ba4

delete command
gcloud artifacts repositories delete quickstart-docker-repo --location=us-central1
==old method
3. tag
docker tag <imageName> gcr.io/<project-id>/<imageName/anything>
4. push to GCP Registry
docker push gcr.io/<project-id>/<imageName/anything-to-put-in-last-step>

5. GO to cloud run, create a new service
==
 python.exe -m pip install --upgrade pip