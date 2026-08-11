import { describe, test, expect } from "bun:test"
import { runCLI } from "./helpers"

function parsedStderr(stderr: string): { error?: string; code?: string } {
  try {
    return JSON.parse(stderr)
  } catch {
    return {}
  }
}

describe("indeed-cli flag validation", () => {
  describe("missing --location", () => {
    test("exits 1 with NO_LOCATION", async () => {
      const result = await runCLI(["search"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("NO_LOCATION")
    })
  })

  describe("--fromage NaN validation", () => {
    test("non-numeric string exits 1 with BAD_ARG", async () => {
      const result = await runCLI(["search", "-l", "New York, NY", "--fromage", "foo"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_ARG")
      expect(err.error).toMatch(/fromage/)
    })

    test("valid integer passes validation (exits 0 or network error, not BAD_ARG)", async () => {
      const result = await runCLI(["search", "-l", "New York, NY", "--fromage", "7", "--limit", "1"])
      const err = parsedStderr(result.stderr)
      expect(err.code).not.toBe("BAD_ARG")
    })
  })

  describe("--radius NaN validation", () => {
    test("non-numeric string exits 1 with BAD_ARG", async () => {
      const result = await runCLI(["search", "-l", "New York, NY", "--radius", "abc"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_ARG")
      expect(err.error).toMatch(/radius/)
    })
  })

  describe("--page NaN validation", () => {
    test("non-numeric string exits 1 with BAD_ARG", async () => {
      const result = await runCLI(["search", "-l", "New York, NY", "--page", "abc"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_ARG")
      expect(err.error).toMatch(/page/)
    })
  })

  describe("--limit NaN validation", () => {
    test("non-numeric string exits 1 with BAD_ARG", async () => {
      const result = await runCLI(["search", "-l", "New York, NY", "--limit", "xyz"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_ARG")
      expect(err.error).toMatch(/limit/)
    })
  })

  describe("detail command", () => {
    test("missing ID exits 1 with NO_ID", async () => {
      const result = await runCLI(["detail"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("NO_ID")
    })

    test("non-key string exits 1 with BAD_ID", async () => {
      const result = await runCLI(["detail", "not-a-key"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_ID")
    })
  })

  describe("unknown command", () => {
    test("exits 1 with BAD_CMD", async () => {
      const result = await runCLI(["foobar"])
      expect(result.exitCode).not.toBe(0)
      const err = parsedStderr(result.stderr)
      expect(err.code).toBe("BAD_CMD")
    })
  })
})
