from django.db import models

class Document(models.Model):
    judul = models.CharField(max_length=255)
    doc = models.TextField()
    kelas = models.CharField(max_length=255)
    fold = models.IntegerField(blank=True,null=True)
    tipe = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return "{}. {}".format(self.id, self.judul)

class Term(models.Model):
    term = models.CharField(max_length=255)

    def __str__(self):
        return "{}. {}".format(self.id, self.term)

class TF(models.Model):
    id_doc = models.IntegerField()
    term = models.CharField(max_length=255)
    tf = models.IntegerField()

    def __str__(self):
        return "{}. {}".format(self.id, self.tf)

class Filter(models.Model):
    term = models.CharField(max_length=255)

    def __str__(self):
        return "{}. {}".format(self.id, self.term)

