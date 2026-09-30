import setuptools

setuptools.setup(
    name="eol_learner_profiles",
    version="0.1.0",
    author="Oficina EOL UChile",
    author_email="eol-ing@uchile.cl",
    description="Eol Learner Profiles",
    long_description="Eol Learner Profiles",
    url="https://eol.uchile.cl",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "eol_learner_profiles": [
            "templates/eol_learner_profiles/*.html",
            "static/eol_learner_profiles/css/*.css",
            "static/eol_learner_profiles/js/*.js",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "lms.djangoapp": [
            "eol_learner_profiles = eol_learner_profiles.apps:EolLearnerProfilesConfig",
        ],
        "cms.djangoapp": [
            "eol_learner_profiles = eol_learner_profiles.apps:EolLearnerProfilesConfig",
        ],
        "openedx.course_tab": [
            "eol_learner_profiles = eol_learner_profiles.plugins:EolLearnerProfileTab",
        ],
        
    },
)
