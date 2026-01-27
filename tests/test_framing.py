# -*- coding: utf-8 -*-
"""
Unit tests for message framing components.

Tests cover:
- AccumulatedBytes: buffer accumulation
- Extraction: delimiter results
- KsumDelimiter: message boundary detection
- DelayedConnection: delay after read
- FramedConnection: loop until complete message
"""
import unittest
from serial_to_mqtt.result.either import Right, Left
from serial_to_mqtt.serial.port import ReceivedBytes, AccumulatedBytes
from serial_to_mqtt.serial.delimiter import Extraction
from serial_to_mqtt.serial.connection import DelayedConnection, FramedConnection
from sokol_sensors.protocols.ksum import KsumDelimiter


class FakeDelay(object):
    """
    Fake delay that counts calls instead of sleeping.

    FakeDelay records how many times wait() was called without
    actually blocking. Used for testing delay-dependent code.

    Example usage:
        delay = FakeDelay()
        delay.wait()
        count = delay.called()  # Returns: 1
    """

    def __init__(self):
        """
        Create a FakeDelay.
        """
        self._called = 0

    def wait(self):
        """
        Record that wait was called.
        """
        self._called = self._called + 1

    def called(self):
        """
        Extract the number of times wait was called.

        Returns:
            int: Call count
        """
        return self._called


class FakeConnection(object):
    """
    Fake connection that returns predefined results.

    FakeConnection returns results from a list in order,
    useful for testing code that reads from connections.

    Example usage:
        results = [Right(ReceivedBytes("data"))]
        fake = FakeConnection(results)
        result = fake.receive()  # Returns first result
    """

    def __init__(self, results):
        """
        Create a FakeConnection with results list.

        Args:
            results: List of Either results to return in order
        """
        self._results = results
        self._index = 0

    def receive(self):
        """
        Return next predefined result.

        Returns:
            Either: Next result from the list
        """
        result = self._results[self._index]
        self._index = self._index + 1
        return result


class AccumulatedBytesAppendsConcatenatedContent(unittest.TestCase):
    """
    Tests that AccumulatedBytes append concatenates content.
    """

    def test(self):
        """
        AccumulatedBytes append concatenates content from ReceivedBytes.
        """
        buffer = AccumulatedBytes("hello")
        result = buffer.append(ReceivedBytes(" world"))
        self.assertEqual(
            "hello world",
            result.content(),
            "AccumulatedBytes append did not concatenate content correctly"
        )


class AccumulatedBytesAppendReturnsNewInstance(unittest.TestCase):
    """
    Tests that AccumulatedBytes append returns new instance.
    """

    def test(self):
        """
        AccumulatedBytes append returns new instance without modifying original.
        """
        buffer = AccumulatedBytes("hello")
        buffer.append(ReceivedBytes(" world"))
        self.assertEqual(
            "hello",
            buffer.content(),
            "AccumulatedBytes original was modified by append"
        )


class AccumulatedBytesTrimKeepsRemainder(unittest.TestCase):
    """
    Tests that AccumulatedBytes trim keeps only remainder.
    """

    def test(self):
        """
        AccumulatedBytes trim keeps only the specified remainder.
        """
        buffer = AccumulatedBytes("hello world")
        result = buffer.trim("world")
        self.assertEqual(
            "world",
            result.content(),
            "AccumulatedBytes trim did not keep remainder correctly"
        )


class AccumulatedBytesEmptyBufferAppends(unittest.TestCase):
    """
    Tests that empty AccumulatedBytes appends data correctly.
    """

    def test(self):
        """
        Empty AccumulatedBytes appends data correctly.
        """
        buffer = AccumulatedBytes("")
        result = buffer.append(ReceivedBytes("data"))
        self.assertEqual(
            "data",
            result.content(),
            "Empty AccumulatedBytes did not append correctly"
        )


class ExtractionEmptyReturnsTrueWhenNoMessages(unittest.TestCase):
    """
    Tests that Extraction empty returns true when no messages.
    """

    def test(self):
        """
        Extraction empty returns true when messages list is empty.
        """
        extraction = Extraction([], "remainder")
        self.assertTrue(
            extraction.empty(),
            "Extraction empty did not return true for empty messages"
        )


class ExtractionEmptyReturnsFalseWhenHasMessages(unittest.TestCase):
    """
    Tests that Extraction empty returns false when has messages.
    """

    def test(self):
        """
        Extraction empty returns false when messages exist.
        """
        extraction = Extraction(["msg"], "")
        self.assertFalse(
            extraction.empty(),
            "Extraction empty returned true when messages exist"
        )


class ExtractionMessagesReturnsList(unittest.TestCase):
    """
    Tests that Extraction messages returns the list.
    """

    def test(self):
        """
        Extraction messages returns the message list.
        """
        extraction = Extraction(["a", "b"], "")
        self.assertEqual(
            ["a", "b"],
            extraction.messages(),
            "Extraction messages did not return correct list"
        )


class ExtractionRemainderReturnsLeftover(unittest.TestCase):
    """
    Tests that Extraction remainder returns leftover bytes.
    """

    def test(self):
        """
        Extraction remainder returns leftover bytes.
        """
        extraction = Extraction([], "leftover")
        self.assertEqual(
            "leftover",
            extraction.remainder(),
            "Extraction remainder did not return correct value"
        )


class KsumDelimiterEmptyInputReturnsEmptyExtraction(unittest.TestCase):
    """
    Tests that KsumDelimiter returns empty extraction for empty input.
    """

    def test(self):
        """
        KsumDelimiter extract returns empty extraction for empty input.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("")
        self.assertTrue(
            extraction.empty(),
            "KsumDelimiter did not return empty extraction for empty input"
        )


class KsumDelimiterEmptyInputHasEmptyRemainder(unittest.TestCase):
    """
    Tests that KsumDelimiter empty input has empty remainder.
    """

    def test(self):
        """
        KsumDelimiter extract empty input has empty remainder.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("")
        self.assertEqual(
            "",
            extraction.remainder(),
            "KsumDelimiter empty input had non-empty remainder"
        )


class KsumDelimiterPartialMessageBuffers(unittest.TestCase):
    """
    Tests that KsumDelimiter buffers partial message without end marker.
    """

    def test(self):
        """
        KsumDelimiter partial message without end marker stays in buffer.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444")
        self.assertTrue(
            extraction.empty(),
            "KsumDelimiter partial message was incorrectly extracted"
        )


class KsumDelimiterPartialMessageKeepsRemainder(unittest.TestCase):
    """
    Tests that KsumDelimiter keeps partial message in remainder.
    """

    def test(self):
        """
        KsumDelimiter partial message kept in remainder.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444")
        self.assertEqual(
            "!1;25.5;38444",
            extraction.remainder(),
            "KsumDelimiter partial message not kept in remainder"
        )


class KsumDelimiterCompleteMessageExtracts(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts complete message with end marker.
    """

    def test(self):
        """
        KsumDelimiter complete message with end marker is extracted.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444\r!2;30")
        self.assertFalse(
            extraction.empty(),
            "KsumDelimiter complete message was not extracted"
        )


class KsumDelimiterCompleteMessageCorrect(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts correct message.
    """

    def test(self):
        """
        KsumDelimiter extracts correct complete message.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444\r!2;30")
        self.assertEqual(
            ["!1;25.5;38444"],
            extraction.messages(),
            "KsumDelimiter extracted wrong message"
        )


class KsumDelimiterCompleteMessageRemainder(unittest.TestCase):
    """
    Tests that KsumDelimiter keeps correct remainder after extraction.
    """

    def test(self):
        """
        KsumDelimiter keeps correct remainder after extraction.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444\r!2;30")
        self.assertEqual(
            "!2;30",
            extraction.remainder(),
            "KsumDelimiter kept wrong remainder"
        )


class KsumDelimiterMultipleMessagesExtractsAll(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts all complete messages.
    """

    def test(self):
        """
        KsumDelimiter multiple complete messages are all extracted.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444\r!2;30.0;12345\r!3;40")
        self.assertEqual(
            ["!1;25.5;38444", "!2;30.0;12345"],
            extraction.messages(),
            "KsumDelimiter did not extract all complete messages"
        )


class KsumDelimiterMultipleMessagesRemainder(unittest.TestCase):
    """
    Tests that KsumDelimiter keeps remainder after multiple messages.
    """

    def test(self):
        """
        KsumDelimiter keeps correct remainder after multiple messages.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;38444\r!2;30.0;12345\r!3;40")
        self.assertEqual(
            "!3;40",
            extraction.remainder(),
            "KsumDelimiter kept wrong remainder after multiple messages"
        )


class KsumDelimiterGarbageBeforeMarkerDiscarded(unittest.TestCase):
    """
    Tests that KsumDelimiter discards garbage before first marker.
    """

    def test(self):
        """
        KsumDelimiter garbage before first marker is discarded.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("garbage!1;25.5;38444\r!2")
        self.assertEqual(
            ["!1;25.5;38444"],
            extraction.messages(),
            "KsumDelimiter message not extracted when garbage precedes"
        )


class KsumDelimiterInvalidStructureSkipped(unittest.TestCase):
    """
    Tests that KsumDelimiter skips invalid message structure.
    """

    def test(self):
        """
        KsumDelimiter invalid message structure is skipped.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!invalid\r!1;25.5;38444\r!2")
        self.assertEqual(
            ["!1;25.5;38444"],
            extraction.messages(),
            "KsumDelimiter valid message not extracted after invalid"
        )


class KsumDelimiterMarkerMessageExtracted(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts marker message with $ value.
    """

    def test(self):
        """
        KsumDelimiter marker message with $ value is extracted.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;$49;38444\r!2;30")
        self.assertEqual(
            ["!1;$49;38444"],
            extraction.messages(),
            "KsumDelimiter marker message not extracted"
        )


class KsumDelimiterPartialChecksumBuffers(unittest.TestCase):
    """
    Tests that KsumDelimiter buffers partial checksum without end marker.
    """

    def test(self):
        """
        KsumDelimiter partial checksum without end marker stays in buffer.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;384")
        self.assertTrue(
            extraction.empty(),
            "KsumDelimiter partial checksum was incorrectly extracted"
        )


class KsumDelimiterNonDigitChecksumInvalid(unittest.TestCase):
    """
    Tests that KsumDelimiter rejects non-digit checksum.
    """

    def test(self):
        """
        KsumDelimiter non-digit checksum makes message invalid.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!1;25.5;abc\r!2;30.0;12345\r!3")
        self.assertEqual(
            ["!2;30.0;12345"],
            extraction.messages(),
            "KsumDelimiter message with non-digit checksum should be skipped"
        )


class KsumDelimiterMissingSemicolonsInvalid(unittest.TestCase):
    """
    Tests that KsumDelimiter rejects message without semicolons.
    """

    def test(self):
        """
        KsumDelimiter message missing semicolons is invalid.
        """
        delimiter = KsumDelimiter()
        extraction = delimiter.extract("!nosemicolons\r!1;25.5;38444\r!2")
        self.assertEqual(
            ["!1;25.5;38444"],
            extraction.messages(),
            "KsumDelimiter message without semicolons should be skipped"
        )


class DelayedConnectionReceiveCallsDelay(unittest.TestCase):
    """
    Tests that DelayedConnection calls delay after read.
    """

    def test(self):
        """
        DelayedConnection receive calls delay wait after reading.
        """
        fake = FakeConnection([Right(ReceivedBytes("data"))])
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delayed.receive()
        self.assertEqual(
            1,
            delay.called(),
            "DelayedConnection did not call delay after receive"
        )


class DelayedConnectionReceiveReturnsInnerResult(unittest.TestCase):
    """
    Tests that DelayedConnection returns inner result.
    """

    def test(self):
        """
        DelayedConnection receive returns result from inner connection.
        """
        fake = FakeConnection([Right(ReceivedBytes("data"))])
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        result = delayed.receive()
        self.assertEqual(
            "data",
            result.value().content(),
            "DelayedConnection inner result not returned correctly"
        )


class DelayedConnectionReceiveReturnsError(unittest.TestCase):
    """
    Tests that DelayedConnection returns error from inner.
    """

    def test(self):
        """
        DelayedConnection receive returns error from inner connection.
        """
        fake = FakeConnection([Left("Connection error")])
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        result = delayed.receive()
        self.assertFalse(
            result.successful(),
            "DelayedConnection error not propagated from inner connection"
        )


class FramedConnectionLoopsUntilComplete(unittest.TestCase):
    """
    Tests that FramedConnection loops until complete message.
    """

    def test(self):
        """
        FramedConnection loops reading until complete message found.
        """
        results = [
            Right(ReceivedBytes("!1;25")),
            Right(ReceivedBytes(".5;38444")),
            Right(ReceivedBytes("\r!2;30"))
        ]
        fake = FakeConnection(results)
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
        result = framed.receive()
        self.assertEqual(
            "!1;25.5;38444",
            result.value().content(),
            "FramedConnection did not assemble complete message from chunks"
        )


class FramedConnectionReturnsErrorOnFailure(unittest.TestCase):
    """
    Tests that FramedConnection returns error if connection fails.
    """

    def test(self):
        """
        FramedConnection returns error if inner connection fails.
        """
        results = [Left("Connection error")]
        fake = FakeConnection(results)
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
        result = framed.receive()
        self.assertFalse(
            result.successful(),
            "FramedConnection error not returned when connection fails"
        )


class FramedConnectionPreservesRemainderFirstMessage(unittest.TestCase):
    """
    Tests that FramedConnection preserves remainder for first message.
    """

    def test(self):
        """
        FramedConnection first message is correct.
        """
        results = [
            Right(ReceivedBytes("!1;25.5;38444\r!2;30.0;12345\r!3")),
            Right(ReceivedBytes(";40.0;99999\r!4"))
        ]
        fake = FakeConnection(results)
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
        first = framed.receive()
        self.assertEqual(
            "!1;25.5;38444",
            first.value().content(),
            "FramedConnection first message not correct"
        )


class FramedConnectionPreservesRemainderSecondMessage(unittest.TestCase):
    """
    Tests that FramedConnection preserves remainder for next call.
    """

    def test(self):
        """
        FramedConnection second message uses preserved remainder.
        """
        results = [
            Right(ReceivedBytes("!1;25.5;38444\r!2;30.0;12345\r!3")),
            Right(ReceivedBytes(";40.0;99999\r!4"))
        ]
        fake = FakeConnection(results)
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
        framed.receive()
        second = framed.receive()
        self.assertEqual(
            "!2;30.0;12345",
            second.value().content(),
            "FramedConnection second message not correct, remainder not preserved"
        )


class FramedConnectionHandlesEmptyReads(unittest.TestCase):
    """
    Tests that FramedConnection handles empty reads between data.
    """

    def test(self):
        """
        FramedConnection handles empty reads while accumulating.
        """
        results = [
            Right(ReceivedBytes("!1;25")),
            Right(ReceivedBytes("")),
            Right(ReceivedBytes(".5;38444")),
            Right(ReceivedBytes("")),
            Right(ReceivedBytes("\r!2"))
        ]
        fake = FakeConnection(results)
        delay = FakeDelay()
        delayed = DelayedConnection(fake, delay)
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
        result = framed.receive()
        self.assertEqual(
            "!1;25.5;38444",
            result.value().content(),
            "FramedConnection message not assembled with empty reads in between"
        )


class KsumDelimiterRealDataExtractsMessages(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts messages from real sensor data.
    """

    def test(self):
        """
        KsumDelimiter extracts messages from dump.txt format.
        """
        delimiter = KsumDelimiter()
        data = "X!1;$49;17145\rX!1;$49;17145\rX!1;$49;17145\rX!1;$49;17145"
        extraction = delimiter.extract(data)
        self.assertEqual(
            3,
            len(extraction.messages()),
            "KsumDelimiter did not extract expected number of messages from real data"
        )


class KsumDelimiterRealDataCorrectMessage(unittest.TestCase):
    """
    Tests that KsumDelimiter extracts correct message content.
    """

    def test(self):
        """
        KsumDelimiter extracts correct message from real data.
        """
        delimiter = KsumDelimiter()
        data = "X!1;$49;17145\rX!1;$49;17145"
        extraction = delimiter.extract(data)
        self.assertEqual(
            "!1;$49;17145",
            extraction.messages()[0],
            "KsumDelimiter extracted wrong message content"
        )


class KsumDelimiterRealDataRemainder(unittest.TestCase):
    """
    Tests that KsumDelimiter keeps correct remainder from real data.
    """

    def test(self):
        """
        KsumDelimiter keeps last partial message as remainder.
        """
        delimiter = KsumDelimiter()
        data = "X!1;$49;17145\rX!1;$49;17145\rX!1;$49"
        extraction = delimiter.extract(data)
        self.assertEqual(
            "X!1;$49",
            extraction.remainder(),
            "KsumDelimiter did not keep correct remainder"
        )


if __name__ == '__main__':
    unittest.main()
