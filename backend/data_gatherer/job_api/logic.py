from django.db.models import Q
from django.db.transaction import atomic
from tqdm import tqdm




@atomic
def initiate_job(job):
    from storage_api.models.data_models import UserHashtagUse, IGUser, Hashtag
    from job_api.models import Job, Task, JobIGUser, JobHashtag, JobUserHashtagUse

    job:Job = job

    print(f"initiating job {job}, gathering data")
    project = job.project

    prj_hashtags = Hashtag.objects.filter(
        project=project
    )
    prj_users = IGUser.objects.filter(
        project=project
    )

    for hashtag in prj_hashtags:
        uses = UserHashtagUse.objects.filter(
            hashtag=hashtag
        ).count()

        if uses == 0:
            prj_hashtags = prj_hashtags.exclude(pk=hashtag.pk)

    for user in prj_users:
        uses = UserHashtagUse.objects.filter(
            igUser=user
        ).count()

        if uses == 0:
            prj_users = prj_users.exclude(pk=user.pk)

    with tqdm(total=prj_users.count(), desc="Creating job users", unit="frame") as pbar:
        for item in prj_users:
            user: IGUser = item
            JobIGUser.objects.create(
                job=job,
                name=user.name
            )
            pbar.update(1)

    n = job.taskGranularity
    chunks = [prj_hashtags[i:i + n] for i in range(0, len(prj_hashtags), n)]
    print(f"There will be {len(chunks)} tasks, granularity: {n}")

    with tqdm(total=len(chunks), desc="Creating tasks", unit="frame") as pbar:
        counter = 1
        for chunk in chunks:
            current_task = Task.objects.create(
                progressiveID=counter,
                inProgress=False,
                isCompleted=False,
                job=job
            )
            for item in chunk:
                hashtag: Hashtag = item
                job_hashtag = JobHashtag.objects.create(
                    job=job,
                    task=current_task,
                    content=hashtag.content
                )

                queryset = UserHashtagUse.objects.filter(
                    project=project,
                    hashtag=hashtag,
                )

                job_users = JobIGUser.objects.filter(job=job)
                with tqdm(total=queryset.count(), desc="Creating associations", unit="frame", leave=False) as pbar2:
                    for j_item in queryset:
                        uhu: UserHashtagUse = j_item
                        JobUserHashtagUse.objects.create(
                            job=job,
                            user=job_users.get(name=uhu.igUser.name),
                            hashtag=job_hashtag,
                            image_path=uhu.image.file.path
                        )
                        pbar2.update(1)

            counter = counter + 1
            pbar.update(1)

    print(f"completed")
    job.isCreated = True
    job.save()
