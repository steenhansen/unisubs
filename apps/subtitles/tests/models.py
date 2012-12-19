# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""Basic sanity tests to make sure the subtitle models aren't completely broken."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from babelsubs.storage import SubtitleSet

from apps.auth.models import CustomUser as User
from apps.subtitles import pipeline
from apps.subtitles.models import SubtitleLanguage, SubtitleVersion
from apps.subtitles.tests.utils import (
    make_video, make_video_2, make_video_3, make_sl, refresh, ids, parent_ids,
    ancestor_ids
)
from apps.teams.models import Team, TeamMember, TeamVideo


class TestSubtitleLanguage(TestCase):
    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()


    def test_create_subtitle_language(self):
        """Basic sanity checks when creating a subtitlelanguage."""
        l = SubtitleLanguage(video=self.video, language_code='en')
        l.save()

        l = refresh(l)
        self.assertEqual(l.language_code, 'en')

    def test_subtitle_language_unique_constraints(self):
        """Test the unique constraints of subtitlelanguages."""

        # The first subtitle language has no restrictions.
        l1 = SubtitleLanguage(video=self.video, language_code='en')
        l1.save()

        # Cannot have more that one SL for the same video+language.
        l2 = SubtitleLanguage(video=self.video, language_code='en')
        self.assertRaises(IntegrityError, lambda: l2.save())

        # But other videos and other languages are fine.
        l3 = SubtitleLanguage(video=self.video2, language_code='en')
        l3.save()

        l4 = SubtitleLanguage(video=self.video, language_code='fr')
        l4.save()

    def test_primary_audio_language(self):
        en = SubtitleLanguage(video=self.video, language_code='en')
        fr = SubtitleLanguage(video=self.video, language_code='fr')
        en.save()
        fr.save()

        en = refresh(en)
        fr = refresh(fr)
        self.assertFalse(en.is_primary_audio_language())
        self.assertFalse(fr.is_primary_audio_language())

        self.video.primary_audio_language_code = 'en'
        self.video.save()

        en = refresh(en)
        fr = refresh(fr)
        self.assertTrue(en.is_primary_audio_language())
        self.assertFalse(fr.is_primary_audio_language())

        self.video.primary_audio_language_code = 'fr'
        self.video.save()

        en = refresh(en)
        fr = refresh(fr)
        self.assertFalse(en.is_primary_audio_language())
        self.assertTrue(fr.is_primary_audio_language())

        self.video.primary_audio_language_code = 'cy'
        self.video.save()

        en = refresh(en)
        fr = refresh(fr)
        self.assertFalse(en.is_primary_audio_language())
        self.assertFalse(fr.is_primary_audio_language())

    def test_get_translation_source(self):
        # Try a language with no versions.
        source_lang = make_sl(self.video, 'en')
        self.assertIsNone(source_lang.get_translation_source_language())

        # Try a non translated language with one version.
        source_lang.add_version()
        source_lang = refresh(source_lang)
        self.assertIsNone(source_lang.get_translation_source_language())

        # Try a non translated language with two versions.  This is different
        # because the lineage map now contains a reference to itself instead of
        # simply being empty.  It still should not be a translation though.
        sv = source_lang.add_version()
        source_lang = refresh(source_lang)
        self.assertIsNone(source_lang.get_translation_source_language())

        # Try a translation.
        translated = make_sl(self.video, 'fr')
        translated.add_version(parents=[sv])
        translated = refresh(translated)
        self.assertEqual(translated.get_translation_source_language(), source_lang)
        self.assertEqual(translated.get_translation_source_language_code(), source_lang.language_code)

    def test_get_tip(self):
        sl = make_sl(self.video, 'en')

        def _assert_tip(public, version_number):
            tip = sl.get_tip(public=public)
            if tip:
                tip = tip.version_number
            self.assertEqual(tip, version_number)

        _assert_tip(False, None)
        _assert_tip(True, None)

        sl.add_version(visibility='private')
        _assert_tip(False, 1)
        _assert_tip(True, None)

        sl.add_version()
        _assert_tip(False, 2)
        _assert_tip(True, 2)

        sl.add_version(visibility='public', visibility_override='private')
        _assert_tip(False, 3)
        _assert_tip(True, 2)

        sl.add_version(visibility='private', visibility_override='private')
        _assert_tip(False, 4)
        _assert_tip(True, 2)

        sl.add_version(visibility='private', visibility_override='public')
        _assert_tip(False, 5)
        _assert_tip(True, 5)

        sl.add_version(visibility='public', visibility_override='public')
        _assert_tip(False, 6)
        _assert_tip(True, 6)

    def test_get_version(self):
        # Actually tests the .version() method whose name we should update at
        # some point to fit with the rest.
        sl_1_en = make_sl(self.video, 'en')
        sl_2_en = make_sl(self.video2, 'en')
        sl_1_fr = make_sl(self.video, 'fr')

        def _assert_version(sl, result, **kwargs):
            version = sl.version(**kwargs)
            if not version:
                actual = None
            else:
                actual = (version.language_code, version.version_number)
            self.assertEqual(result, actual)

        # version() always returns None if there are no versions at all
        _assert_version(sl_1_en, None)
        _assert_version(sl_2_en, None)
        _assert_version(sl_1_fr, None)

        _assert_version(sl_1_en, None, public_only=True)
        _assert_version(sl_1_en, None, public_only=False)
        _assert_version(sl_1_en, None, version_number=1)

        # unless you ask for a specific version you get the latest one
        sl_1_en.add_version(visibility='public')
        sl_1_en.add_version(visibility='public')
        sl_2_en.add_version(visibility='public')
        _assert_version(sl_1_en, ('en', 2))
        _assert_version(sl_2_en, ('en', 1))
        _assert_version(sl_1_fr, None)

        # public_only is on by default
        sl_1_en.add_version(visibility='private')
        sl_2_en.add_version(visibility='private', visibility_override='public')
        sl_1_fr.add_version(visibility='public', visibility_override='private')
        _assert_version(sl_1_en, ('en', 2))
        _assert_version(sl_2_en, ('en', 2))
        _assert_version(sl_1_fr, None)

        # but can be turned off
        _assert_version(sl_1_en, ('en', 3), public_only=False)
        _assert_version(sl_2_en, ('en', 2), public_only=False)
        _assert_version(sl_1_fr, ('fr', 1), public_only=False)

        # you can ask for specific versions
        _assert_version(sl_1_en, ('en', 3), public_only=False, version_number=3)
        _assert_version(sl_1_en, ('en', 2), public_only=False, version_number=2)
        _assert_version(sl_1_en, ('en', 1), public_only=False, version_number=1)

        # but they may not be found if they're invalid, or private and you don't
        # override public_only
        _assert_version(sl_1_en, None, version_number=0)
        _assert_version(sl_1_en, None, version_number=3)
        _assert_version(sl_1_en, None, version_number=2023)


class TestSubtitleVersion(TestCase):
    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()
        self.sl_en = make_sl(self.video, 'en')
        self.sl_is = make_sl(self.video, 'is')


    def test_create_subtitle_version(self):
        """Basic sanity checks when creating a version."""

        sv = self.sl_en.add_version(title='title a', description='desc a',
                                    subtitles=[])

        sv = refresh(sv)

        self.assertEqual(sv.language_code, 'en')
        self.assertEqual(sv.video.id, self.video.id)
        self.assertEqual(sv.subtitle_language.id, self.sl_en.id)
        self.assertEqual(sv.title, 'title a')
        self.assertEqual(sv.description, 'desc a')
        self.assertEqual(list(sv.get_subtitles().subtitle_items()), [])
        self.assertEqual(sv.visibility, 'public')

    def test_subtitle_serialization(self):
        """Test basic subtitle serialization."""

        # Empty SubtitleSets
        # We explicitly test before and after refreshing to make sure the
        # serialization happens properly in both cases.
        sv = self.sl_en.add_version(subtitles=SubtitleSet('en'))
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))

        sv = self.sl_en.add_version(subtitles=None)
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))

        sv = self.sl_en.add_version(subtitles=[])
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet('en'))

        # Non-empty SubtitleSets
        # Again we test pre- and post-refresh.  Note that this is also checking
        # the equality handling for Subtitle and SubtitleSets.
        s0 = (100, 200, "a")
        s1 = (300, 400, "b")

        sv = self.sl_en.add_version(subtitles=SubtitleSet.from_list('en', [s0, s1]))
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list('en', [s0, s1]))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list('en', [s0, s1]))

        sv = self.sl_en.add_version(subtitles=[s0, s1])
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list('en', [s0, s1]))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list('en', [s0, s1]))

    def test_denormalization_sanity_checks(self):
        """Test the sanity checks for data denormalized into the version model."""

        # Version videos must match their subtitlelanguage's videos.
        sv = self.sl_en.add_version()
        sv.video = self.video2
        self.assertRaises(AssertionError, lambda: sv.save())

        # Version language codes must match their subtitlelanguage's language
        # codes.
        sv = self.sl_en.add_version()
        sv.language_code = 'fr'
        self.assertRaises(AssertionError, lambda: sv.save())

    def test_visibility(self):
        """Test the (non-overrided) visibility filtering of versions."""

        sv1 = self.sl_en.add_version()
        sv2 = self.sl_en.add_version()
        sv3 = self.sl_en.add_version()

        def _count_public():
            return self.sl_en.subtitleversion_set.public().count()

        self.assertEqual(3, _count_public())
        self.assertTrue(sv1.is_public())
        self.assertFalse(sv1.is_private())
        self.assertTrue(sv2.is_public())
        self.assertFalse(sv2.is_private())
        self.assertTrue(sv3.is_public())
        self.assertFalse(sv3.is_private())

        sv1.visibility = 'private'
        sv1.save()
        self.assertEqual(2, _count_public())
        self.assertFalse(sv1.is_public())
        self.assertTrue(sv1.is_private())

        sv3.visibility = 'private'
        sv3.save()
        self.assertEqual(1, _count_public())
        self.assertFalse(sv3.is_public())
        self.assertTrue(sv3.is_private())

        sv2.visibility = 'private'
        sv2.save()
        self.assertEqual(0, _count_public())
        self.assertFalse(sv2.is_public())
        self.assertTrue(sv2.is_private())

    def test_visibility_override(self):
        """Test the overrided visibility filtering of versions."""

        sv = self.sl_en.add_version()

        def _count_public():
            return self.sl_en.subtitleversion_set.public().count()

        # vis     override
        # public  null
        self.assertEqual(1, _count_public())
        self.assertTrue(sv.is_public())
        self.assertFalse(sv.is_private())

        # vis     override
        # private null
        sv.visibility = 'private'
        sv.save()
        self.assertEqual(0, _count_public())
        self.assertFalse(sv.is_public())
        self.assertTrue(sv.is_private())

        # vis     override
        # private public
        sv.visibility_override = 'public'
        sv.save()
        self.assertEqual(1, _count_public())
        self.assertTrue(sv.is_public())
        self.assertFalse(sv.is_private())

        # vis     override
        # public  public
        sv.visibility = 'public'
        sv.save()
        self.assertEqual(1, _count_public())
        self.assertTrue(sv.is_public())
        self.assertFalse(sv.is_private())

        # vis     override
        # public  private
        sv.visibility_override = 'private'
        sv.save()
        self.assertEqual(0, _count_public())
        self.assertFalse(sv.is_public())
        self.assertTrue(sv.is_private())

        # vis     override
        # private private
        sv.visibility = 'private'
        sv.save()
        self.assertEqual(0, _count_public())
        self.assertFalse(sv.is_public())
        self.assertTrue(sv.is_private())

    def test_text_time_change(self):
        from subtitles.pipeline import add_subtitles

        SubtitleVersion.objects.all().delete()
        SubtitleLanguage.objects.all().delete()

        subtitles_1 = [
            (0, 1000, 'Hello there'),
        ]
        subtitles_2 = [
            (0, 1000, 'Hello there'),
            (2000, 3000, 'How are you?'),
        ]
        subtitles_3 = [
            (0, 1000, 'Hello there.'),
            (2000, 3000, 'How are you?'),
        ]
        subtitles_4 = [
            (0, 1000, 'Hello there.'),
            (2000, 4000, 'How are you?'),
        ]

        sv1 = add_subtitles(self.video, 'en', subtitles_1)
        sv2 = add_subtitles(self.video, 'en', subtitles_2)
        sv3 = add_subtitles(self.video, 'en', subtitles_3)
        sv4 = add_subtitles(self.video, 'en', subtitles_4)
        assert sv4 # Shut up, Pyflakes.

        self.assertEquals((1.0, 1.0), sv1.get_changes())
        # 50% of text and 50% of timing is new
        self.assertEquals((0.5, 0.5), sv2.get_changes())
        self.assertEquals((0.0, 0.5), sv3.get_changes())

        # TODO: This will break.
        # self.assertEquals((0.5, 0.0), sv4.get_changes())

    def test_subtitle_count(self):
        s0 = (100, 200, "a")
        s1 = (300, 400, "b")

        sv1 = self.sl_en.add_version(subtitles=[])
        sv2 = self.sl_en.add_version(subtitles=[s0])
        sv3 = self.sl_en.add_version(subtitles=[s0, s1])

        self.assertEqual(0, sv1.subtitle_count)
        self.assertEqual(1, sv2.subtitle_count)
        self.assertEqual(2, sv3.subtitle_count)

        sv1 = refresh(sv1)
        sv2 = refresh(sv2)
        sv3 = refresh(sv3)

        self.assertEqual(0, sv1.subtitle_count)
        self.assertEqual(1, sv2.subtitle_count)
        self.assertEqual(2, sv3.subtitle_count)

        sv4 = self.sl_en.add_version(subtitles=[(None, None, str(i))
                                                for i in xrange(200)])
        self.assertEqual(200, sv4.subtitle_count)
        sv4 = refresh(sv4)
        self.assertEqual(200, sv4.subtitle_count)

    def test_sibling_set(self):
        def _assert_siblings(sv, *vns):
            siblings = sv.sibling_set.order_by('version_number')

            for v in siblings:
                self.assertEqual(sv.subtitle_language_id, v.subtitle_language_id)

            self.assertEqual([v.version_number for v in siblings], list(vns))

        v = self.sl_en.add_version()
        _assert_siblings(v, 1)

        v = self.sl_en.add_version()
        _assert_siblings(v, 1, 2)

        v = self.sl_en.add_version()
        _assert_siblings(v, 1, 2, 3)

        v = self.sl_is.add_version()
        _assert_siblings(v, 1)

        v = self.sl_en.add_version()
        _assert_siblings(v, 1, 2, 3, 4)

    def test_rollback_data(self):
        def _assert_rollback_info(v, rollback_of_version_number, is_rollback,
                                  get_rollback_source):
            self.assertEqual(v.rollback_of_version_number,
                             rollback_of_version_number)

            self.assertEqual(v.is_rollback(), is_rollback)

            if get_rollback_source:
                self.assertEqual(v.get_rollback_source().id,
                                 get_rollback_source.id)
            else:
                self.assertIsNone(v.get_rollback_source())

        # Two normal versions.
        v1 = self.sl_en.add_version(subtitles=[])
        _assert_rollback_info(v1, None, False, None)

        v2 = self.sl_en.add_version(subtitles=[])
        _assert_rollback_info(v2, None, False, None)

        # Simulate a legacy rollback.
        v3 = self.sl_en.add_version(subtitles=[], rollback_of_version_number=0)
        _assert_rollback_info(v3, 0, True, None)

        # Add a normal one on top.
        v4 = self.sl_en.add_version(subtitles=[])
        _assert_rollback_info(v4, None, False, None)

        # Now add a new-style rollback.
        v5 = self.sl_en.add_version(subtitles=[], rollback_of_version_number=2)
        _assert_rollback_info(v5, 2, True, v2)

        # Add another normal one on top.
        v6 = self.sl_en.add_version(subtitles=[])
        _assert_rollback_info(v6, None, False, None)

        # Rollbacks to rollbacks are cool I guess.
        v7 = self.sl_en.add_version(subtitles=[], rollback_of_version_number=5)
        _assert_rollback_info(v7, 5, True, v5)

        # Make sure the sanity checks work.
        crazy = SubtitleVersion(version_number=4, rollback_of_version_number=4)
        self.assertRaises(ValidationError, lambda: crazy.full_clean())

        crazy = SubtitleVersion(version_number=4, rollback_of_version_number=200)
        self.assertRaises(ValidationError, lambda: crazy.full_clean())


class TestHistory(TestCase):
    def setUp(self):
        self.video = make_video()

        self.sl_en = make_sl(self.video, 'en')
        self.sl_fr = make_sl(self.video, 'fr')
        self.sl_de = make_sl(self.video, 'de')
        self.sl_cy = make_sl(self.video, 'cy')


    def test_linear_parents(self):
        """Test the ancestry, parentage, and lineage for a simple linear history."""

        sv1 = self.sl_en.add_version()
        sv2 = self.sl_en.add_version()
        sv3 = self.sl_en.add_version()

        sv1 = refresh(sv1)
        sv2 = refresh(sv2)
        sv3 = refresh(sv3)

        self.assertEqual(parent_ids(sv1), ids([]))
        self.assertEqual(parent_ids(sv2), ids([sv1]))
        self.assertEqual(parent_ids(sv3), ids([sv2]))

        self.assertEqual(ids(sv1.get_ancestors()), ids([]))
        self.assertEqual(ids(sv2.get_ancestors()), ids([sv1]))
        self.assertEqual(ids(sv3.get_ancestors()), ids([sv1, sv2]))

        self.assertEqual(sv1.lineage, {})
        self.assertEqual(sv2.lineage, {'en': 1})
        self.assertEqual(sv3.lineage, {'en': 2})

    def test_multiple_parents(self):
        """Test the ancestry, parentage, and lineage for a merged history."""

        # en fr
        #    4
        #    |
        #    3
        #   /|
        #  3 |
        #  | 2
        #  2 |
        #  | 1
        #  |/
        #  1
        e1 = self.sl_en.add_version()
        f1 = self.sl_fr.add_version(parents=[e1])
        e2 = self.sl_en.add_version()
        f2 = self.sl_fr.add_version()
        e3 = self.sl_en.add_version()
        f3 = self.sl_fr.add_version(parents=[e3])
        f4 = self.sl_fr.add_version()

        e1 = refresh(e1)
        e2 = refresh(e2)
        e3 = refresh(e3)
        f1 = refresh(f1)
        f2 = refresh(f2)
        f3 = refresh(f3)
        f4 = refresh(f4)

        # Parents
        self.assertEqual(parent_ids(e1), ids([]))
        self.assertEqual(parent_ids(f1), ids([e1]))

        self.assertEqual(parent_ids(e2), ids([e1]))
        self.assertEqual(parent_ids(f2), ids([f1]))

        self.assertEqual(parent_ids(e3), ids([e2]))
        self.assertEqual(parent_ids(f3), ids([f2, e3]))

        self.assertEqual(parent_ids(f4), ids([f3]))

        # Ancestors
        self.assertEqual(ancestor_ids(e1), ids([]))
        self.assertEqual(ancestor_ids(e2), ids([e1]))
        self.assertEqual(ancestor_ids(e3), ids([e1, e2]))

        self.assertEqual(ancestor_ids(f1), ids([e1]))
        self.assertEqual(ancestor_ids(f2), ids([e1, f1]))
        self.assertEqual(ancestor_ids(f3), ids([e1, f1, e2, f2, e3]))
        self.assertEqual(ancestor_ids(f4), ids([e1, f1, e2, f2, e3, f3]))

        # Lineage
        self.assertEqual(e1.lineage, {})
        self.assertEqual(e2.lineage, {'en': 1})
        self.assertEqual(e3.lineage, {'en': 2})

        self.assertEqual(f1.lineage, {'en': 1})
        self.assertEqual(f2.lineage, {'en': 1, 'fr': 1})
        self.assertEqual(f3.lineage, {'en': 3, 'fr': 2})
        self.assertEqual(f4.lineage, {'en': 3, 'fr': 3})

    def test_tangled_history(self):
        """Test the ancestry, parentage, and lineage for a terrifying history."""

        # en fr de cy
        #
        #    3
        #    |
        #    |     5
        #    |    /|
        #    |   / |
        #    |  7  |
        #    |  |\ |
        #    |  | \|
        # +--|--|--4
        # |  |  |  |
        # 3  |  |  |
        # |  |  |  |
        # |  |  6  |
        # |  |  |\ |
        # |  |  | \|
        # |  |  |  3
        # |  |  | /|
        # |  |  |/ |
        # |  |  5  |
        # |  |  |  2
        # |  |  4  |
        # |  | /|\ |
        # |  |/ | \|
        # |  |  |  1
        # |  |  | /
        # |  |  |/
        # |  |  3
        # |  |  |
        # |  2  |
        # |  |  |
        # +--|--2
        # |  | /|
        # 2  |/ |
        # |  1  |
        # |     |
        # +-----1
        # |
        # 1

        e1 = self.sl_en.add_version(parents=[])
        d1 = self.sl_de.add_version(parents=[e1])
        f1 = self.sl_fr.add_version(parents=[])
        e2 = self.sl_en.add_version(parents=[])
        d2 = self.sl_de.add_version(parents=[f1, e2])
        f2 = self.sl_fr.add_version(parents=[])
        d3 = self.sl_de.add_version(parents=[])
        c1 = self.sl_cy.add_version(parents=[d3])
        d4 = self.sl_de.add_version(parents=[f2, c1])
        c2 = self.sl_cy.add_version(parents=[])
        d5 = self.sl_de.add_version(parents=[])
        c3 = self.sl_cy.add_version(parents=[d5])
        d6 = self.sl_de.add_version(parents=[c3])
        e3 = self.sl_en.add_version(parents=[])
        c4 = self.sl_cy.add_version(parents=[e3])
        d7 = self.sl_de.add_version(parents=[c4])
        c5 = self.sl_cy.add_version(parents=[d7])
        f3 = self.sl_fr.add_version(parents=[])

        e1 = refresh(e1)
        d1 = refresh(d1)
        f1 = refresh(f1)
        e2 = refresh(e2)
        d2 = refresh(d2)
        f2 = refresh(f2)
        d3 = refresh(d3)
        c1 = refresh(c1)
        d4 = refresh(d4)
        c2 = refresh(c2)
        d5 = refresh(d5)
        c3 = refresh(c3)
        d6 = refresh(d6)
        e3 = refresh(e3)
        c4 = refresh(c4)
        d7 = refresh(d7)
        c5 = refresh(c5)
        f3 = refresh(f3)

        # Parents
        self.assertEqual(parent_ids(e1), ids([]))
        self.assertEqual(parent_ids(d1), ids([e1]))
        self.assertEqual(parent_ids(f1), ids([]))
        self.assertEqual(parent_ids(e2), ids([e1]))
        self.assertEqual(parent_ids(d2), ids([d1, e2, f1]))
        self.assertEqual(parent_ids(f2), ids([f1]))
        self.assertEqual(parent_ids(d3), ids([d2]))
        self.assertEqual(parent_ids(c1), ids([d3]))
        self.assertEqual(parent_ids(d4), ids([f2, d3, c1]))
        self.assertEqual(parent_ids(c2), ids([c1]))
        self.assertEqual(parent_ids(d5), ids([d4]))
        self.assertEqual(parent_ids(c3), ids([d5, c2]))
        self.assertEqual(parent_ids(d6), ids([d5, c3]))
        self.assertEqual(parent_ids(e3), ids([e2]))
        self.assertEqual(parent_ids(c4), ids([c3, e3]))
        self.assertEqual(parent_ids(d7), ids([d6, c4]))
        self.assertEqual(parent_ids(c5), ids([c4, d7]))
        self.assertEqual(parent_ids(f3), ids([f2]))

        # Ancestors
        self.assertEqual(ancestor_ids(e1), ids([]))
        self.assertEqual(ancestor_ids(d1), ids([e1]))
        self.assertEqual(ancestor_ids(f1), ids([]))
        self.assertEqual(ancestor_ids(e2), ids([e1]))
        self.assertEqual(ancestor_ids(d2), ids([e1, e2, f1, d1]))
        self.assertEqual(ancestor_ids(f2), ids([f1]))
        self.assertEqual(ancestor_ids(d3), ids([e1, e2, f1, d1, d2]))
        self.assertEqual(ancestor_ids(c1), ids([e1, e2, f1, d1, d2, d3]))
        self.assertEqual(ancestor_ids(d4), ids([e1, e2, f1, f2, d1, d2, d3, c1]))
        self.assertEqual(ancestor_ids(c2), ids([e1, e2, f1, d1, d2, d3, c1]))
        self.assertEqual(ancestor_ids(d5), ids([e1, e2, f1, f2, d1, d2, d3, d4, c1]))
        self.assertEqual(ancestor_ids(c3), ids([e1, e2, f1, f2, d1, d2, d3, d4, d5, c1, c2]))
        self.assertEqual(ancestor_ids(d6), ids([e1, e2, f1, f2, d1, d2, d3, d4, d5, c1, c2, c3]))
        self.assertEqual(ancestor_ids(e3), ids([e1, e2]))
        self.assertEqual(ancestor_ids(c4), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, c1, c2, c3]))
        self.assertEqual(ancestor_ids(d7), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, d6, c1, c2, c3, c4]))
        self.assertEqual(ancestor_ids(c5), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, d6, d7, c1, c2, c3, c4]))
        self.assertEqual(ancestor_ids(f3), ids([f1, f2]))

        # Lineage
        self.assertEqual(e1.lineage, {})
        self.assertEqual(d1.lineage, {'en': 1})
        self.assertEqual(f1.lineage, {})
        self.assertEqual(e2.lineage, {'en': 1})
        self.assertEqual(d2.lineage, {'en': 2, 'fr': 1, 'de': 1})
        self.assertEqual(f2.lineage, {'fr': 1})
        self.assertEqual(d3.lineage, {'en': 2, 'fr': 1, 'de': 2})
        self.assertEqual(c1.lineage, {'en': 2, 'fr': 1, 'de': 3})
        self.assertEqual(d4.lineage, {'en': 2, 'fr': 2, 'de': 3, 'cy': 1})
        self.assertEqual(c2.lineage, {'en': 2, 'fr': 1, 'de': 3, 'cy': 1})
        self.assertEqual(d5.lineage, {'en': 2, 'fr': 2, 'de': 4, 'cy': 1})
        self.assertEqual(c3.lineage, {'en': 2, 'fr': 2, 'de': 5, 'cy': 2})
        self.assertEqual(d6.lineage, {'en': 2, 'fr': 2, 'de': 5, 'cy': 3})
        self.assertEqual(e3.lineage, {'en': 2})
        self.assertEqual(c4.lineage, {'en': 3, 'fr': 2, 'de': 5, 'cy': 3})
        self.assertEqual(d7.lineage, {'en': 3, 'fr': 2, 'de': 6, 'cy': 4})
        self.assertEqual(c5.lineage, {'en': 3, 'fr': 2, 'de': 7, 'cy': 4})
        self.assertEqual(f3.lineage, {'fr': 2})


class TestSubtitleLanguageHavingQueries(TestCase):
    """Test the [not_]having[_public/_nonempty]_versions methods of the SL manager.

    They contain raw SQL through extra() calls, so need to be carefully tested.

    """

    def _get(self, qs, video=None):
        if video:
            qs = qs.filter(video=video)

        return sorted([sl.language_code for sl in qs])

    def _get_langs(self, video=None):
        qs = SubtitleLanguage.objects.having_versions()
        return self._get(qs, video)

    def _get_public_langs(self, video=None):
        qs = SubtitleLanguage.objects.having_public_versions()
        return self._get(qs, video)

    def _get_not_langs(self, video=None):
        qs = SubtitleLanguage.objects.not_having_versions()
        return self._get(qs, video)

    def _get_not_public_langs(self, video=None):
        qs = SubtitleLanguage.objects.not_having_public_versions()
        return self._get(qs, video)

    def _get_nonempty_langs(self, video=None):
        qs = SubtitleLanguage.objects.having_nonempty_versions()
        return self._get(qs, video)

    def _get_not_nonempty_langs(self, video=None):
        qs = SubtitleLanguage.objects.not_having_nonempty_versions()
        return self._get(qs, video)

    def _get_nonempty_tip_langs(self, video=None):
        qs = SubtitleLanguage.objects.having_nonempty_tip()
        return self._get(qs, video)

    def _get_not_nonempty_tip_langs(self, video=None):
        qs = SubtitleLanguage.objects.not_having_nonempty_tip()
        return self._get(qs, video)


    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()

        self.sl_1_en = make_sl(self.video, 'en')
        self.sl_1_fr = make_sl(self.video, 'fr')
        self.sl_2_en = make_sl(self.video2, 'en')
        self.sl_2_cy = make_sl(self.video2, 'cy')


    def test_having_versions(self):
        # No versions at all.
        self.assertEqual(self._get_langs(),            [])
        self.assertEqual(self._get_langs(self.video),  [])
        self.assertEqual(self._get_langs(self.video2), [])

        # A version for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_langs(),            ['en'])
        self.assertEqual(self._get_langs(self.video),  ['en'])
        self.assertEqual(self._get_langs(self.video2), [])

        # Two versions for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_langs(),            ['en'])
        self.assertEqual(self._get_langs(self.video),  ['en'])
        self.assertEqual(self._get_langs(self.video2), [])

        # Version for 2/cy.
        self.sl_2_cy.add_version()

        self.assertEqual(self._get_langs(),            ['cy', 'en'])
        self.assertEqual(self._get_langs(self.video),  ['en'])
        self.assertEqual(self._get_langs(self.video2), ['cy'])

        # Version for 2/en.
        self.sl_2_en.add_version()

        self.assertEqual(self._get_langs(),            ['cy', 'en', 'en'])
        self.assertEqual(self._get_langs(self.video),  ['en'])
        self.assertEqual(self._get_langs(self.video2), ['cy', 'en'])

        # Version for 1/fr.
        self.sl_1_fr.add_version()

        self.assertEqual(self._get_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_langs(self.video2), ['cy', 'en'])

        # Ensure making them private doesn't affect anything here.
        v = self.sl_2_cy.get_tip()
        v.visibility = 'private'
        v.save()

        v = self.sl_2_en.get_tip()
        v.visibility_override = 'private'
        v.save()

        v = self.sl_1_fr.get_tip()
        v.visibility = 'private'
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_langs(self.video2), ['cy', 'en'])

    def test_not_having_versions(self):
        # No versions at all.
        self.assertEqual(self._get_not_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_not_langs(self.video2), ['cy', 'en'])

        # A version for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_not_langs(),            ['cy', 'en', 'fr'])
        self.assertEqual(self._get_not_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_langs(self.video2), ['cy', 'en'])

        # Two versions for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_not_langs(),            ['cy', 'en', 'fr'])
        self.assertEqual(self._get_not_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_langs(self.video2), ['cy', 'en'])

        # Version for 2/cy.
        self.sl_2_cy.add_version()

        self.assertEqual(self._get_not_langs(),            ['en', 'fr'])
        self.assertEqual(self._get_not_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_langs(self.video2), ['en'])

        # Version for 2/en.
        self.sl_2_en.add_version()

        self.assertEqual(self._get_not_langs(),            ['fr'])
        self.assertEqual(self._get_not_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_langs(self.video2), [])

        # Version for 1/fr.
        self.sl_1_fr.add_version()

        self.assertEqual(self._get_not_langs(),            [])
        self.assertEqual(self._get_not_langs(self.video),  [])
        self.assertEqual(self._get_not_langs(self.video2), [])

        # Ensure making them private doesn't affect anything here.
        v = self.sl_2_cy.get_tip()
        v.visibility = 'private'
        v.save()

        v = self.sl_2_en.get_tip()
        v.visibility_override = 'private'
        v.save()

        v = self.sl_1_fr.get_tip()
        v.visibility = 'private'
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_not_langs(),            [])
        self.assertEqual(self._get_not_langs(self.video),  [])
        self.assertEqual(self._get_not_langs(self.video2), [])


    def test_having_public_versions(self):
        # No versions at all.
        self.assertEqual(self._get_public_langs(),            [])
        self.assertEqual(self._get_public_langs(self.video),  [])
        self.assertEqual(self._get_public_langs(self.video2), [])

        # A version for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_public_langs(),            ['en'])
        self.assertEqual(self._get_public_langs(self.video),  ['en'])
        self.assertEqual(self._get_public_langs(self.video2), [])

        # Two versions for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_public_langs(),            ['en'])
        self.assertEqual(self._get_public_langs(self.video),  ['en'])
        self.assertEqual(self._get_public_langs(self.video2), [])

        # Version for 2/cy.
        self.sl_2_cy.add_version()

        self.assertEqual(self._get_public_langs(),            ['cy', 'en'])
        self.assertEqual(self._get_public_langs(self.video),  ['en'])
        self.assertEqual(self._get_public_langs(self.video2), ['cy'])

        # Version for 2/en.
        self.sl_2_en.add_version()

        self.assertEqual(self._get_public_langs(),            ['cy', 'en', 'en'])
        self.assertEqual(self._get_public_langs(self.video),  ['en'])
        self.assertEqual(self._get_public_langs(self.video2), ['cy', 'en'])

        # Version for 1/fr.
        self.sl_1_fr.add_version()

        self.assertEqual(self._get_public_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video2), ['cy', 'en'])

        # Ensure making *one* of the two 1/en versions private doesn't affect anything.
        v = self.sl_1_en.get_tip()
        v.visibility = 'private'
        v.save()

        self.assertEqual(self._get_public_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video2), ['cy', 'en'])

        # But making all of the versions in a language private filters it.
        v = self.sl_2_cy.get_tip()
        v.visibility = 'private'
        v.save()

        self.assertEqual(self._get_public_langs(),            ['en', 'en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video2), ['en'])

        v = self.sl_2_en.get_tip()
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_public_langs(),            ['en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_public_langs(self.video2), [])

        v = self.sl_1_fr.get_tip()
        v.visibility = 'private'
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_public_langs(),            ['en'])
        self.assertEqual(self._get_public_langs(self.video),  ['en'])
        self.assertEqual(self._get_public_langs(self.video2), [])

    def test_not_having_public_versions(self):
        # No versions at all.
        self.assertEqual(self._get_not_public_langs(),            ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy', 'en'])

        # A version for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_not_public_langs(),            ['cy', 'en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy', 'en'])

        # Two versions for 1/en.
        self.sl_1_en.add_version()

        self.assertEqual(self._get_not_public_langs(),            ['cy', 'en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy', 'en'])

        # Version for 2/cy.
        self.sl_2_cy.add_version()

        self.assertEqual(self._get_not_public_langs(),            ['en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), ['en'])

        # Version for 2/en.
        self.sl_2_en.add_version()

        self.assertEqual(self._get_not_public_langs(),            ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), [])

        # Version for 1/fr.
        self.sl_1_fr.add_version()

        self.assertEqual(self._get_not_public_langs(),            [])
        self.assertEqual(self._get_not_public_langs(self.video),  [])
        self.assertEqual(self._get_not_public_langs(self.video2), [])

        # Ensure making *one* of the two 1/en versions private doesn't affect anything.
        v = self.sl_1_en.get_tip()
        v.visibility = 'private'
        v.save()

        self.assertEqual(self._get_not_public_langs(),            [])
        self.assertEqual(self._get_not_public_langs(self.video),  [])
        self.assertEqual(self._get_not_public_langs(self.video2), [])

        # But making all of the versions in a language private unfilters it.
        v = self.sl_2_cy.get_tip()
        v.visibility = 'private'
        v.save()

        self.assertEqual(self._get_not_public_langs(),            ['cy'])
        self.assertEqual(self._get_not_public_langs(self.video),  [])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy'])

        v = self.sl_2_en.get_tip()
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_not_public_langs(),            ['cy', 'en'])
        self.assertEqual(self._get_not_public_langs(self.video),  [])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy', 'en'])

        v = self.sl_1_fr.get_tip()
        v.visibility = 'private'
        v.visibility_override = 'private'
        v.save()

        self.assertEqual(self._get_not_public_langs(),            ['cy', 'en', 'fr'])
        self.assertEqual(self._get_not_public_langs(self.video),  ['fr'])
        self.assertEqual(self._get_not_public_langs(self.video2), ['cy', 'en'])


    def test_having_nonempty_versions(self):
        v1 = self.video
        v2 = self.video2

        # Having no versions at all obviously means there are no nonempty ones.
        self.assertEqual(self._get_nonempty_langs(),   [])
        self.assertEqual(self._get_nonempty_langs(v1), [])
        self.assertEqual(self._get_nonempty_langs(v2), [])

        # Empty versions don't count toward this queryset.
        self.sl_1_en.add_version()
        self.sl_2_cy.add_version(subtitles=[])

        self.assertEqual(self._get_nonempty_langs(),   [])
        self.assertEqual(self._get_nonempty_langs(v1), [])
        self.assertEqual(self._get_nonempty_langs(v2), [])

        # Nonempty versions DO count toward this queryset.
        self.sl_1_en.add_version(subtitles=[(None, None, "foo")])
        self.sl_1_fr.add_version(subtitles=[(100, 200, "bar"), (200, 300, "bar")])

        self.assertEqual(self._get_nonempty_langs(),   ['en', 'fr'])
        self.assertEqual(self._get_nonempty_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_nonempty_langs(v2), [])

        # These querysets check all versions, not just tips.
        self.sl_1_en.add_version(subtitles=[])
        self.sl_1_fr.add_version(subtitles=[])

        self.assertEqual(self._get_nonempty_langs(),   ['en', 'fr'])
        self.assertEqual(self._get_nonempty_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_nonempty_langs(v2), [])

    def test_not_having_nonempty_versions(self):
        v1 = self.video
        v2 = self.video2

        # Having no versions at all fits the bill -- these languages have no
        # nonempty versions.
        self.assertEqual(self._get_not_nonempty_langs(),   ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_nonempty_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_not_nonempty_langs(v2), ['cy', 'en'])

        # Empty versions don't count toward this queryset.
        self.sl_1_en.add_version()
        self.sl_2_cy.add_version(subtitles=[])

        self.assertEqual(self._get_not_nonempty_langs(),   ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_nonempty_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_not_nonempty_langs(v2), ['cy', 'en'])

        # Nonempty versions DO count toward this queryset.
        self.sl_1_en.add_version(subtitles=[(None, None, "foo")])
        self.sl_1_fr.add_version(subtitles=[(100, 200, "bar"), (200, 300, "bar")])

        self.assertEqual(self._get_not_nonempty_langs(),   ['cy', 'en'])
        self.assertEqual(self._get_not_nonempty_langs(v1), [])
        self.assertEqual(self._get_not_nonempty_langs(v2), ['cy', 'en'])

        # These querysets check all versions, not just tips.
        self.sl_1_en.add_version(subtitles=[])
        self.sl_1_fr.add_version(subtitles=[])

        self.assertEqual(self._get_not_nonempty_langs(),   ['cy', 'en'])
        self.assertEqual(self._get_not_nonempty_langs(v1), [])
        self.assertEqual(self._get_not_nonempty_langs(v2), ['cy', 'en'])


    def test_having_nonempty_tip(self):
        v1 = self.video
        v2 = self.video2

        # Having no versions at all obviously means there are none with a valid
        # tip.
        self.assertEqual(self._get_nonempty_tip_langs(),   [])
        self.assertEqual(self._get_nonempty_tip_langs(v1), [])
        self.assertEqual(self._get_nonempty_tip_langs(v2), [])

        # Empty versions don't count toward this queryset.
        self.sl_1_en.add_version()
        self.sl_2_cy.add_version(subtitles=[])

        self.assertEqual(self._get_nonempty_tip_langs(),   [])
        self.assertEqual(self._get_nonempty_tip_langs(v1), [])
        self.assertEqual(self._get_nonempty_tip_langs(v2), [])

        # Nonempty versions DO count toward this queryset.
        self.sl_1_en.add_version(subtitles=[(None, None, "foo")])
        self.sl_1_fr.add_version(subtitles=[(100, 200, "bar"), (200, 300, "bar")])

        self.assertEqual(self._get_nonempty_tip_langs(),   ['en', 'fr'])
        self.assertEqual(self._get_nonempty_tip_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_nonempty_tip_langs(v2), [])

        # These querysets check just the tips.
        self.sl_1_en.add_version(subtitles=[])

        self.assertEqual(self._get_nonempty_tip_langs(),   ['fr'])
        self.assertEqual(self._get_nonempty_tip_langs(v1), ['fr'])
        self.assertEqual(self._get_nonempty_tip_langs(v2), [])

    def test_not_having_nonempty_tip(self):
        v1 = self.video
        v2 = self.video2

        # Having no versions at all means they do not have "a non-empty tip".
        self.assertEqual(self._get_not_nonempty_tip_langs(),   ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v2), ['cy', 'en'])

        # Empty versions don't count toward this queryset.
        self.sl_1_en.add_version()
        self.sl_2_cy.add_version(subtitles=[])

        self.assertEqual(self._get_not_nonempty_tip_langs(),   ['cy', 'en', 'en', 'fr'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v1), ['en', 'fr'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v2), ['cy', 'en'])

        # Nonempty versions DO count toward this queryset.
        self.sl_1_fr.add_version(subtitles=[(100, 200, "bar"), (200, 300, "bar")])
        self.sl_1_en.add_version(subtitles=[(None, None, "foo")])

        self.assertEqual(self._get_not_nonempty_tip_langs(),   ['cy', 'en'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v1), [])
        self.assertEqual(self._get_not_nonempty_tip_langs(v2), ['cy', 'en'])

        # These querysets check just the tips.
        self.sl_1_en.add_version(subtitles=[])

        self.assertEqual(self._get_not_nonempty_tip_langs(),   ['cy', 'en', 'en'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v1), ['en'])
        self.assertEqual(self._get_not_nonempty_tip_langs(v2), ['cy', 'en'])


class TestTeamInteractions(TestCase):
    def setUp(self):
        users = User.objects.all()

        self.user1 = users[0]
        self.user2 = users[1]
        self.user_public = users[2]

        self.team1 = Team.objects.create(name='One', slug='one')
        self.team2 = Team.objects.create(name='Two', slug='two')

        TeamMember.objects.create(user=self.user1, team=self.team1)
        TeamMember.objects.create(user=self.user2, team=self.team2)

        self.video1 = make_video()
        self.video2 = make_video_2()
        self.video_public = make_video_3()

        TeamVideo.objects.create(video=self.video1, team=self.team1,
                                 added_by=User.get_anonymous())
        TeamVideo.objects.create(video=self.video2, team=self.team2,
                                 added_by=User.get_anonymous())

        self.en1 = make_sl(self.video1, 'en')
        self.en2 = make_sl(self.video2, 'en')
        self.en_public = make_sl(self.video_public, 'en')

        self.fr1 = make_sl(self.video1, 'fr')
        self.fr2 = make_sl(self.video2, 'fr')
        self.fr_public = make_sl(self.video_public, 'fr')


    def test_private_versions(self):
        def _get_versions(sl, user):
            return sorted([version.version_number
                           for version in sl.versions_for_user(user)])

        def _add(video, language_code, visibility, visibility_override):
            return pipeline.add_subtitles(video, language_code, '',
                                          visibility=visibility,
                                          visibility_override=visibility_override)


        # Alias stuff.
        u1, u2, up = self.user1, self.user2, self.user_public
        en1, en2, enp = self.en1, self.en2, self.en_public
        fr1, fr2, frp = self.fr1, self.fr2, self.fr_public
        v1, v2, vp = self.video1, self.video2, self.video_public

        # Ensure everything starts blank.
        self.assertEqual(_get_versions(en1, u1), [])
        self.assertEqual(_get_versions(en2, u1), [])
        self.assertEqual(_get_versions(enp, u1), [])

        self.assertEqual(_get_versions(en1, u2), [])
        self.assertEqual(_get_versions(en2, u2), [])
        self.assertEqual(_get_versions(enp, u2), [])

        self.assertEqual(_get_versions(en1, up), [])
        self.assertEqual(_get_versions(en2, up), [])
        self.assertEqual(_get_versions(enp, up), [])

        # Everyone can see versions on non-team videos, regardless of visibility
        # settings.
        _add(vp, 'en', 'public', '')
        _add(vp, 'en', 'private', '')
        _add(vp, 'en', 'public', 'private')
        _add(vp, 'en', 'private', 'private')
        _add(vp, 'en', 'public', 'public')
        _add(vp, 'en', 'private', 'public')

        self.assertEqual(_get_versions(enp, u1), [1, 2, 3, 4, 5, 6])
        self.assertEqual(_get_versions(enp, u2), [1, 2, 3, 4, 5, 6])
        self.assertEqual(_get_versions(enp, up), [1, 2, 3, 4, 5, 6])

        # Team videos can always be seen by their team members.  If they're
        # private, *only* their team members can see them.
        _add(v1, 'en', 'public', '')
        _add(v1, 'en', 'private', '')
        _add(v1, 'en', 'public', 'private')
        _add(v1, 'en', 'private', 'private')
        _add(v1, 'en', 'public', 'public')
        _add(v1, 'en', 'private', 'public')

        self.assertEqual(_get_versions(en1, u1), [1, 2, 3, 4, 5, 6])
        self.assertEqual(_get_versions(en1, u2), [1, 5, 6])
        self.assertEqual(_get_versions(en1, up), [1, 5, 6])

        # Should work on any team/language.
        _add(v2, 'fr', 'public', '')
        _add(v2, 'fr', 'private', '')
        _add(v2, 'fr', 'public', 'private')
        _add(v2, 'fr', 'private', 'private')
        _add(v2, 'fr', 'public', 'public')
        _add(v2, 'fr', 'private', 'public')

        self.assertEqual(_get_versions(fr2, u1), [1, 5, 6])
        self.assertEqual(_get_versions(fr2, u2), [1, 2, 3, 4, 5, 6])
        self.assertEqual(_get_versions(fr2, up), [1, 5, 6])


class TestSubtitleMetadata(TestCase):
    fixtures = ['staging_users.json', 'staging_videos.json']

    def setUp(self):
        self.video = make_video()
        self.sl_en = make_sl(self.video, 'en')
        self.user = User.objects.all()[0]

    def test_reviewed_by_setting(self):
        version = self.sl_en.add_version()

        self.assertEqual(version.get_reviewed_by(), None,
            "Version's reviewed_by metadata is not originally None.")

        version.set_reviewed_by(self.user)

        self.assertEqual(version.get_reviewed_by().pk, self.user.pk,
            "Version's reviewed_by metadata is not the correct User.")

        version = refresh(version)

        self.assertEqual(version.get_reviewed_by().pk, self.user.pk,
            "Version's reviewed_by metadata is not the correct User.")

        version = self.sl_en.add_version()

        self.assertEqual(version.get_reviewed_by(), None,
            "Versions should not inherit reviewed_by metadata.")

    def test_approved_by_setting(self):
        version = self.sl_en.add_version()

        self.assertEqual(version.get_approved_by(), None,
            "Version's approved_by metadata is not originally None.")

        version.set_approved_by(self.user)

        self.assertEqual(version.get_approved_by().pk, self.user.pk,
            "Version's approved_by metadata is not the correct User.")

        version = refresh(version)

        self.assertEqual(version.get_approved_by().pk, self.user.pk,
            "Version's approved_by metadata is not the correct User.")

        version = self.sl_en.add_version()

        self.assertEqual(version.get_approved_by(), None,
            "Versions should not inherit approved_by metadata.")
