(() => {
  "use strict";

  const MATERIALS = {
    steel: {
      name: "Structural Steel",
      E: 200000,
      allowable: 165,
      density: 7850,
      cost: 85000
    },
    timber: {
      name: "Engineered Timber",
      E: 11000,
      allowable: 12,
      density: 520,
      cost: 52000
    },
    aluminum: {
      name: "Aluminum",
      E: 69000,
      allowable: 95,
      density: 2700,
      cost: 110000
    }
  };

  const MISSIONS = [
    {
      title: "Neighborhood Connector",
      story: "A growing riverside community needs a dependable local crossing.",
      span: 10,
      load: 420,
      budget: 420000,
      difficulty: "ROOKIE"
    },
    {
      title: "Industrial Access",
      story: "Heavy service vehicles need reliable access to a new logistics yard.",
      span: 12,
      load: 600,
      budget: 520000,
      difficulty: "ROOKIE"
    },
    {
      title: "Mountain Supply Route",
      story: "Design for longer reach and heavier traffic with limited material access.",
      span: 14,
      load: 780,
      budget: 650000,
      difficulty: "INTERMEDIATE"
    },
    {
      title: "Urban Flyover Link",
      story: "A busy urban corridor needs a compact but efficient structural solution.",
      span: 16,
      load: 980,
      budget: 780000,
      difficulty: "INTERMEDIATE"
    },
    {
      title: "Emergency Relief Crossing",
      story: "Rapid deployment is required, but safety and cost limits still apply.",
      span: 18,
      load: 1200,
      budget: 920000,
      difficulty: "ADVANCED"
    },
    {
      title: "Regional Freight Bridge",
      story: "Your final contract carries the heaviest load across the longest span.",
      span: 20,
      load: 1500,
      budget: 1120000,
      difficulty: "EXPERT"
    }
  ];

  const $ = (id) => document.getElementById(id);
  const els = {
    level: $("levelValue"),
    xp: $("xpValue"),
    xpBar: $("xpBar"),
    score: $("scoreValue"),
    missionNumber: $("missionNumber"),
    difficulty: $("difficultyBadge"),
    missionTitle: $("missionTitle"),
    missionStory: $("missionStory"),
    missionSpan: $("missionSpan"),
    missionLoad: $("missionLoad"),
    missionBudget: $("missionBudget"),
    attempts: $("attemptsValue"),
    width: $("widthRange"),
    depth: $("depthRange"),
    girders: $("girderRange"),
    widthOut: $("widthOut"),
    depthOut: $("depthOut"),
    girderOut: $("girderOut"),
    costPreview: $("costPreview"),
    massPreview: $("massPreview"),
    budgetPreview: $("budgetPreview"),
    testBtn: $("testBtn"),
    resetDesignBtn: $("resetDesignBtn"),
    resetCampaignBtn: $("resetCampaignBtn"),
    soundBtn: $("soundBtn"),
    helpBtn: $("helpBtn"),
    simStatus: $("simStatus"),
    arena: $("arena"),
    deckPath: $("deckPath"),
    girderPath: $("girderPath"),
    bridgeStructure: $("bridgeStructure"),
    truss: $("trussGroup"),
    truck: $("truck"),
    loadArrow: $("loadArrow"),
    loadArrowText: $("loadArrowText"),
    utilValue: $("utilValue"),
    utilBar: $("utilBar"),
    stressValue: $("stressValue"),
    stressLimit: $("stressLimit"),
    deflectionValue: $("deflectionValue"),
    deflectionLimit: $("deflectionLimit"),
    costValue: $("costValue"),
    costLimit: $("costLimit"),
    safetyValue: $("safetyValue"),
    safetySub: $("safetySub"),
    eventLog: $("eventLog"),
    campaignTrack: $("campaignTrack"),
    grade: $("gradeValue"),
    ratingTitle: $("ratingTitle"),
    ratingText: $("ratingText"),
    bestScore: $("bestScoreValue"),
    resultDialog: $("resultDialog"),
    dialogIcon: $("dialogIcon"),
    dialogKicker: $("dialogKicker"),
    dialogTitle: $("dialogTitle"),
    dialogMessage: $("dialogMessage"),
    scoreBreakdown: $("scoreBreakdown"),
    closeResultBtn: $("closeResultBtn"),
    nextMissionBtn: $("nextMissionBtn"),
    helpDialog: $("helpDialog"),
    closeHelpBtn: $("closeHelpBtn")
  };

  const DEFAULT_STATE = {
    missionIndex: 0,
    unlocked: 0,
    score: 0,
    xp: 0,
    bestScores: [0, 0, 0, 0, 0, 0],
    completed: [false, false, false, false, false, false],
    attempts: 3,
    sound: true
  };

  let state = loadState();
  let testing = false;
  let dialogAction = "next";
  let audioContext = null;

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem("buildsafe-v2"));
      if (!saved) return structuredCloneSafe(DEFAULT_STATE);
      return {
        ...structuredCloneSafe(DEFAULT_STATE),
        ...saved,
        bestScores: Array.isArray(saved.bestScores) ? saved.bestScores.slice(0, 6).concat([0,0,0,0,0,0]).slice(0,6) : [...DEFAULT_STATE.bestScores],
        completed: Array.isArray(saved.completed) ? saved.completed.slice(0, 6).concat([false,false,false,false,false,false]).slice(0,6) : [...DEFAULT_STATE.completed]
      };
    } catch {
      return structuredCloneSafe(DEFAULT_STATE);
    }
  }

  function structuredCloneSafe(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function saveState() {
    try {
      localStorage.setItem("buildsafe-v2", JSON.stringify(state));
    } catch {}
  }

  function peso(value) {
    return "₱" + Math.round(value).toLocaleString("en-PH");
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function getSelectedMaterial() {
    const input = document.querySelector('input[name="material"]:checked');
    return MATERIALS[input ? input.value : "steel"];
  }

  function mission() {
    return MISSIONS[state.missionIndex];
  }

  function currentDesign() {
    return {
      width: Number(els.width.value),
      depth: Number(els.depth.value),
      girders: Number(els.girders.value),
      material: getSelectedMaterial()
    };
  }

  function computeDesign() {
    const m = mission();
    const d = currentDesign();
    const L = m.span * 1000;
    const Ptotal = m.load * 1000;
    const P = Ptotal / d.girders;
    const I = d.width * Math.pow(d.depth, 3) / 12;
    const M = P * L / 4;
    const stress = M * (d.depth / 2) / I;
    const deflection = P * Math.pow(L, 3) / (48 * d.material.E * I);
    const deflectionLimit = L / 360;
    const volumeEach = (d.width / 1000) * (d.depth / 1000) * m.span;
    const totalVolume = volumeEach * d.girders;
    const massKg = totalVolume * d.material.density;
    const deckAndConnections = m.span * 9000 + d.girders * 14000;
    const cost = totalVolume * d.material.cost + deckAndConnections;
    const stressRatio = stress / d.material.allowable;
    const deflectionRatio = deflection / deflectionLimit;
    const utilization = Math.max(stressRatio, deflectionRatio);
    const budgetRatio = cost / m.budget;
    const pass = stressRatio <= 1 && deflectionRatio <= 1 && budgetRatio <= 1;

    return {
      ...d,
      stress,
      deflection,
      deflectionLimit,
      cost,
      massKg,
      stressRatio,
      deflectionRatio,
      utilization,
      budgetRatio,
      pass
    };
  }

  function renderMission() {
    const m = mission();
    els.missionNumber.textContent = "MISSION " + String(state.missionIndex + 1).padStart(2, "0");
    els.difficulty.textContent = m.difficulty;
    els.missionTitle.textContent = m.title;
    els.missionStory.textContent = m.story;
    els.missionSpan.textContent = m.span.toFixed(1) + " m";
    els.missionLoad.textContent = m.load.toLocaleString() + " kN";
    els.missionBudget.textContent = peso(m.budget);
    els.attempts.textContent = state.attempts;
    els.loadArrowText.textContent = m.load.toLocaleString() + " kN";
    renderCampaign();
    renderPlayer();
    resetTelemetry();
    updatePreview();
    logEvent("JOB", "Contract loaded: " + m.title + ".");
  }

  function renderPlayer() {
    const level = Math.floor(state.xp / 500) + 1;
    const within = state.xp % 500;
    els.level.textContent = level;
    els.xp.textContent = within + " / 500";
    els.xpBar.style.width = (within / 5) + "%";
    els.score.textContent = state.score.toLocaleString();
    const best = Math.max(...state.bestScores);
    els.bestScore.textContent = best.toLocaleString();

    let grade = "C";
    let title = "Junior Designer";
    let text = "Complete missions safely and efficiently to improve your rating.";
    const completedCount = state.completed.filter(Boolean).length;
    if (completedCount >= 2 || state.score >= 900) {
      grade = "B";
      title = "Project Engineer";
      text = "Your designs are becoming consistently safe and cost-aware.";
    }
    if (completedCount >= 4 || state.score >= 2200) {
      grade = "A";
      title = "Senior Engineer";
      text = "You are balancing structural performance and project economics.";
    }
    if (completedCount === 6 && state.score >= 3500) {
      grade = "S";
      title = "Chief Bridge Engineer";
      text = "Campaign cleared with high engineering efficiency.";
    }
    els.grade.textContent = grade;
    els.ratingTitle.textContent = title;
    els.ratingText.textContent = text;
  }

  function renderCampaign() {
    els.campaignTrack.innerHTML = "";
    MISSIONS.forEach((item, index) => {
      const node = document.createElement("button");
      node.type = "button";
      node.className =
        "mission-node" +
        (state.completed[index] ? " complete" : "") +
        (index === state.missionIndex ? " active" : "") +
        (index > state.unlocked ? " locked" : "");
      node.disabled = index > state.unlocked;
      const score = state.bestScores[index] || 0;
      node.innerHTML =
        "<span>MISSION " + String(index + 1).padStart(2, "0") + "</span>" +
        "<strong>" + item.title + "</strong>" +
        "<em>" + (state.completed[index] ? "✓ " + score.toLocaleString() + " pts" : index > state.unlocked ? "LOCKED" : "AVAILABLE") + "</em>";
      node.addEventListener("click", () => {
        if (testing || index > state.unlocked) return;
        state.missionIndex = index;
        state.attempts = 3;
        saveState();
        resetDesign();
        renderMission();
      });
      els.campaignTrack.appendChild(node);
    });
  }

  function updatePreview() {
    const r = computeDesign();
    els.widthOut.textContent = r.width + " mm";
    els.depthOut.textContent = r.depth + " mm";
    els.girderOut.textContent = r.girders;
    els.costPreview.textContent = peso(r.cost);
    els.massPreview.textContent = (r.massKg / 1000).toFixed(1) + " t";
    els.budgetPreview.textContent = Math.round(r.budgetRatio * 100) + "%";
    els.budgetPreview.style.color = r.budgetRatio > 1 ? "var(--red)" : r.budgetRatio > .9 ? "var(--yellow)" : "";
    previewBridge(r);
  }

  function previewBridge(r) {
    const depthVisual = clamp((r.depth - 250) / 950, 0, 1);
    const trussOpacity = 0.28 + depthVisual * 0.72;
    els.truss.style.opacity = String(trussOpacity);
    const width = 3 + Math.min(8, r.girders * 1.2);
    els.girderPath.style.strokeWidth = width + "px";
  }

  function resetTelemetry() {
    els.stressValue.textContent = "—";
    els.stressLimit.textContent = "Limit —";
    els.deflectionValue.textContent = "—";
    els.deflectionLimit.textContent = "Limit —";
    els.costValue.textContent = "—";
    els.costLimit.textContent = "Budget " + peso(mission().budget);
    els.safetyValue.textContent = "READY";
    els.safetySub.textContent = "Awaiting load test";
    setTelemetryState(0, "");
    setTelemetryState(1, "");
    setTelemetryState(2, "");
    setTelemetryState(3, "");
    setUtilization(0);
    setBridgeSag(0, false);
    setStatus("DESIGN MODE", "");
    els.truck.setAttribute("transform", "translate(70 177)");
    els.loadArrow.classList.remove("active");
  }

  function setTelemetryState(index, stateName) {
    const card = document.querySelectorAll(".telemetry article")[index];
    card.classList.remove("good", "bad", "warn");
    if (stateName) card.classList.add(stateName);
  }

  function setUtilization(ratio) {
    const pct = Math.round(ratio * 100);
    els.utilValue.textContent = pct + "%";
    els.utilBar.style.width = clamp(pct, 0, 115) / 1.15 + "%";
    if (ratio > 1) els.utilBar.style.background = "var(--red)";
    else if (ratio > .92) els.utilBar.style.background = "var(--yellow)";
    else if (ratio >= .68) els.utilBar.style.background = "var(--green)";
    else els.utilBar.style.background = "var(--blue)";
  }

  function setBridgeSag(ratio, failed) {
    const sag = clamp(ratio, 0, 1.35) * 28;
    const deckY = 210 + sag;
    const girderY = 225 + sag;
    els.deckPath.setAttribute("d", "M130 210 Q450 " + deckY.toFixed(1) + " 770 210");
    els.girderPath.setAttribute("d", "M130 225 Q450 " + girderY.toFixed(1) + " 770 225");
    const color = failed ? "#ff6470" : ratio > .92 ? "#f7c948" : "#dfe8ef";
    els.deckPath.style.stroke = color;
    els.girderPath.style.stroke = failed ? "#d94c57" : ratio > .92 ? "#c7a442" : "#6d8296";
    els.truss.querySelectorAll("path").forEach((path) => {
      path.style.stroke = failed ? "#b8444e" : ratio > .92 ? "#8f7a3b" : "#3d5b75";
    });
  }

  function setStatus(text, type) {
    els.simStatus.classList.remove("testing", "pass", "fail");
    if (type) els.simStatus.classList.add(type);
    els.simStatus.querySelector("span").textContent = text;
  }

  function logEvent(code, message) {
    const row = document.createElement("div");
    const t = document.createElement("time");
    const s = document.createElement("span");
    t.textContent = code;
    s.textContent = message;
    row.append(t, s);
    els.eventLog.prepend(row);
    while (els.eventLog.children.length > 7) {
      els.eventLog.removeChild(els.eventLog.lastElementChild);
    }
  }

  function tone(freq = 440, duration = .08, gainValue = .04) {
    if (!state.sound) return;
    try {
      audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(gainValue, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(.0001, audioContext.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioContext.destination);
      osc.start();
      osc.stop(audioContext.currentTime + duration);
    } catch {}
  }

  async function runLoadTest() {
    if (testing) return;
    testing = true;
    document.body.classList.add("testing");
    els.testBtn.disabled = true;

    const result = computeDesign();
    const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const duration = reduced ? 450 : 3200;
    const start = performance.now();

    setStatus("LOAD TEST RUNNING", "testing");
    logEvent("TEST", "Design load entering bridge.");
    tone(330, .07);
    els.loadArrow.classList.add("active");

    await new Promise((resolve) => {
      function frame(now) {
        const p = clamp((now - start) / duration, 0, 1);
        const x = 70 + p * 650;
        els.truck.setAttribute("transform", "translate(" + x.toFixed(1) + " 177)");
        const bell = Math.sin(Math.PI * p);
        const instantaneous = result.utilization * bell;
        setBridgeSag(instantaneous, false);
        setUtilization(instantaneous);

        if (p > .43 && p < .57) {
          els.loadArrow.classList.add("active");
        } else {
          els.loadArrow.classList.remove("active");
        }

        if (p < 1) requestAnimationFrame(frame);
        else resolve();
      }
      requestAnimationFrame(frame);
    });

    finalizeTest(result);
    testing = false;
    document.body.classList.remove("testing");
    els.testBtn.disabled = false;
  }

  function finalizeTest(r) {
    els.stressValue.textContent = r.stress.toFixed(1) + " MPa";
    els.stressLimit.textContent = "Limit " + r.material.allowable.toFixed(0) + " MPa";
    els.deflectionValue.textContent = r.deflection.toFixed(1) + " mm";
    els.deflectionLimit.textContent = "Limit " + r.deflectionLimit.toFixed(1) + " mm";
    els.costValue.textContent = peso(r.cost);
    els.costLimit.textContent = "Budget " + peso(mission().budget);

    setTelemetryState(0, r.stressRatio <= 1 ? (r.stressRatio > .92 ? "warn" : "good") : "bad");
    setTelemetryState(1, r.deflectionRatio <= 1 ? (r.deflectionRatio > .92 ? "warn" : "good") : "bad");
    setTelemetryState(2, r.budgetRatio <= 1 ? (r.budgetRatio > .92 ? "warn" : "good") : "bad");
    setUtilization(r.utilization);
    setBridgeSag(r.utilization, !r.pass);

    if (r.pass) {
      const structuralEfficiency = Math.round(clamp(100 - Math.abs(r.utilization - .84) * 150, 35, 100));
      const costEfficiency = Math.round(clamp(120 - r.budgetRatio * 80, 20, 100));
      const attemptBonus = state.attempts * 25;
      const missionScore = Math.round(150 + structuralEfficiency * 2 + costEfficiency * 1.5 + attemptBonus);
      const xpGain = Math.round(100 + missionScore * .2);

      state.score += missionScore;
      state.xp += xpGain;
      state.bestScores[state.missionIndex] = Math.max(state.bestScores[state.missionIndex], missionScore);
      state.completed[state.missionIndex] = true;
      if (state.missionIndex < MISSIONS.length - 1) {
        state.unlocked = Math.max(state.unlocked, state.missionIndex + 1);
      }
      saveState();
      renderPlayer();
      renderCampaign();

      setStatus("BRIDGE APPROVED", "pass");
      els.safetyValue.textContent = "PASS";
      els.safetySub.textContent = "All mission limits satisfied";
      setTelemetryState(3, "good");
      logEvent("PASS", "Inspection complete. Bridge accepted.");
      tone(660, .11);
      setTimeout(() => tone(880, .13), 100);

      showResult({
        pass: true,
        title: state.missionIndex === MISSIONS.length - 1 ? "Campaign Contract Cleared" : "Bridge Approved",
        message: "Safe, serviceable and within budget. Your engineering efficiency earned " + missionScore.toLocaleString() + " points.",
        items: [
          ["MISSION SCORE", missionScore.toLocaleString()],
          ["XP EARNED", "+" + xpGain],
          ["UTILIZATION", Math.round(r.utilization * 100) + "%"]
        ]
      });
    } else {
      state.attempts = Math.max(0, state.attempts - 1);
      saveState();
      els.attempts.textContent = state.attempts;
      setStatus("TEST FAILED", "fail");
      els.safetyValue.textContent = "FAIL";
      els.safetySub.textContent = failureReason(r);
      setTelemetryState(3, "bad");
      logEvent("FAIL", failureReason(r));
      els.arena.classList.add("shake");
      setTimeout(() => els.arena.classList.remove("shake"), 800);
      tone(150, .18, .06);

      if (state.attempts === 0) {
        showResult({
          pass: false,
          exhausted: true,
          title: "Contract Paused",
          message: "All three test attempts were used. Restart the mission, revise the design and try again.",
          items: [
            ["STRESS", Math.round(r.stressRatio * 100) + "%"],
            ["DEFLECTION", Math.round(r.deflectionRatio * 100) + "%"],
            ["BUDGET", Math.round(r.budgetRatio * 100) + "%"]
          ]
        });
      } else {
        showResult({
          pass: false,
          title: "Load Test Failed",
          message: failureReason(r) + " You have " + state.attempts + " attempt" + (state.attempts === 1 ? "" : "s") + " remaining.",
          items: [
            ["STRESS", Math.round(r.stressRatio * 100) + "%"],
            ["DEFLECTION", Math.round(r.deflectionRatio * 100) + "%"],
            ["BUDGET", Math.round(r.budgetRatio * 100) + "%"]
          ]
        });
      }
    }
  }

  function failureReason(r) {
    const reasons = [];
    if (r.stressRatio > 1) reasons.push("bending stress exceeded the allowable limit");
    if (r.deflectionRatio > 1) reasons.push("deflection exceeded L/360");
    if (r.budgetRatio > 1) reasons.push("project cost exceeded the budget");
    if (!reasons.length) return "Design requires revision.";
    return reasons.map((x, i) => (i === 0 ? x[0].toUpperCase() + x.slice(1) : x)).join("; ") + ".";
  }

  function showResult({ pass, exhausted = false, title, message, items }) {
    els.dialogIcon.textContent = pass ? "✓" : "!";
    els.dialogIcon.style.color = pass ? "var(--green)" : "var(--red)";
    els.dialogIcon.style.background = pass ? "rgba(81,216,138,.12)" : "rgba(255,100,112,.12)";
    els.dialogIcon.style.borderColor = pass ? "rgba(81,216,138,.35)" : "rgba(255,100,112,.35)";
    els.dialogKicker.textContent = pass ? "LOAD TEST COMPLETE" : exhausted ? "MISSION ATTEMPTS USED" : "STRUCTURAL REVIEW";
    els.dialogTitle.textContent = title;
    els.dialogMessage.textContent = message;
    els.scoreBreakdown.innerHTML = items.map(([label, value]) =>
      "<div><span>" + label + "</span><strong>" + value + "</strong></div>"
    ).join("");

    if (pass) {
      dialogAction = "next";
      els.nextMissionBtn.hidden = false;
      els.nextMissionBtn.textContent = state.missionIndex < MISSIONS.length - 1 ? "Next mission →" : "Replay final mission";
    } else if (exhausted) {
      dialogAction = "restart";
      els.nextMissionBtn.hidden = false;
      els.nextMissionBtn.textContent = "Restart mission";
    } else {
      dialogAction = "review";
      els.nextMissionBtn.hidden = true;
    }

    if (typeof els.resultDialog.showModal === "function") els.resultDialog.showModal();
    else els.resultDialog.setAttribute("open", "");
  }

  function closeDialog(dialog) {
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
  }

  function resetDesign() {
    document.querySelector('input[name="material"][value="steel"]').checked = true;
    els.width.value = "250";
    els.depth.value = "500";
    els.girders.value = "2";
    resetTelemetry();
    updatePreview();
    logEvent("LAB", "Design reset to baseline section.");
  }

  function goNext() {
    if (dialogAction === "restart") {
      state.attempts = 3;
      saveState();
      closeDialog(els.resultDialog);
      resetDesign();
      renderMission();
      return;
    }

    if (dialogAction === "next") {
      if (state.missionIndex < MISSIONS.length - 1) {
        state.missionIndex += 1;
      }
      state.attempts = 3;
      saveState();
      closeDialog(els.resultDialog);
      resetDesign();
      renderMission();
    }
  }

  function resetCampaign() {
    const ok = window.confirm("Reset all BuildSafe campaign progress, scores and XP?");
    if (!ok) return;
    state = structuredCloneSafe(DEFAULT_STATE);
    saveState();
    resetDesign();
    renderMission();
    renderPlayer();
    renderCampaign();
    logEvent("SYS", "Campaign progress reset.");
  }

  [els.width, els.depth, els.girders].forEach((input) => {
    input.addEventListener("input", updatePreview);
  });

  document.querySelectorAll('input[name="material"]').forEach((input) => {
    input.addEventListener("change", updatePreview);
  });

  els.testBtn.addEventListener("click", runLoadTest);
  els.resetDesignBtn.addEventListener("click", resetDesign);
  els.resetCampaignBtn.addEventListener("click", resetCampaign);
  els.closeResultBtn.addEventListener("click", () => closeDialog(els.resultDialog));
  els.nextMissionBtn.addEventListener("click", goNext);

  els.helpBtn.addEventListener("click", () => {
    if (typeof els.helpDialog.showModal === "function") els.helpDialog.showModal();
    else els.helpDialog.setAttribute("open", "");
  });
  els.closeHelpBtn.addEventListener("click", () => closeDialog(els.helpDialog));

  els.soundBtn.addEventListener("click", () => {
    state.sound = !state.sound;
    els.soundBtn.textContent = state.sound ? "🔊" : "🔇";
    els.soundBtn.setAttribute("aria-label", state.sound ? "Mute sound" : "Enable sound");
    saveState();
    if (state.sound) tone(520, .06);
  });

  els.resultDialog.addEventListener("click", (event) => {
    if (event.target === els.resultDialog) closeDialog(els.resultDialog);
  });
  els.helpDialog.addEventListener("click", (event) => {
    if (event.target === els.helpDialog) closeDialog(els.helpDialog);
  });

  els.soundBtn.textContent = state.sound ? "🔊" : "🔇";
  renderMission();
  renderPlayer();
  renderCampaign();
})();