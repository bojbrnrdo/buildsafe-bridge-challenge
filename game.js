(() => {
  "use strict";

  const MATERIALS = {
    steel: {
      name: "Steel I-girder",
      E: 200000,
      stressLimit: 165,
      density: 7850,
      areaFactor: 0.12,
      inertiaFactor: 0.42,
      costPerKg: 85,
      costPerM3: null
    },
    timber: {
      name: "Glulam timber",
      E: 11000,
      stressLimit: 12,
      density: 520,
      areaFactor: 1,
      inertiaFactor: 1,
      costPerKg: null,
      costPerM3: 75000
    },
    aluminum: {
      name: "Aluminum box",
      E: 69000,
      stressLimit: 90,
      density: 2700,
      areaFactor: 0.16,
      inertiaFactor: 0.55,
      costPerKg: 320,
      costPerM3: null
    }
  };

  const MISSIONS = [
    {
      title: "Neighborhood Connector",
      story: "Design a safe two-lane bridge for a growing riverside community.",
      span: 10,
      load: 420,
      budget: 1550000,
      difficulty: "ROOKIE",
      suggested: { material: "steel", width: 300, depth: 700, girders: 4 }
    },
    {
      title: "Industrial Access",
      story: "Service trucks need a dependable crossing into a new logistics yard.",
      span: 12,
      load: 650,
      budget: 2150000,
      difficulty: "ROOKIE",
      suggested: { material: "steel", width: 320, depth: 800, girders: 4 }
    },
    {
      title: "Mountain Supply Route",
      story: "A longer span must carry heavier vehicles with limited project funds.",
      span: 14,
      load: 820,
      budget: 2800000,
      difficulty: "INTERMEDIATE",
      suggested: { material: "steel", width: 340, depth: 900, girders: 5 }
    },
    {
      title: "Urban Flyover Link",
      story: "Design an efficient bridge for a busy urban corridor and tighter clearances.",
      span: 16,
      load: 1000,
      budget: 3500000,
      difficulty: "INTERMEDIATE",
      suggested: { material: "steel", width: 360, depth: 980, girders: 5 }
    },
    {
      title: "Emergency Relief Crossing",
      story: "Heavy relief vehicles need a safe crossing with little room for redesign.",
      span: 18,
      load: 1250,
      budget: 4900000,
      difficulty: "ADVANCED",
      suggested: { material: "steel", width: 380, depth: 1080, girders: 6 }
    },
    {
      title: "Regional Freight Bridge",
      story: "Complete the campaign with the longest span and the heaviest design vehicle.",
      span: 20,
      load: 1500,
      budget: 6000000,
      difficulty: "EXPERT",
      suggested: { material: "steel", width: 400, depth: 1180, girders: 6 }
    }
  ];

  const PRESETS = {
    economy: { width: 260, depth: 600, girders: 3 },
    balanced: { width: 300, depth: 700, girders: 4 },
    heavy: { width: 400, depth: 950, girders: 6 }
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
    widthDiagram: $("widthDiagram"),
    depthDiagram: $("depthDiagram"),
    sectionShape: $("sectionShape"),
    girderMassPreview: $("girderMassPreview"),
    deadLoadPreview: $("deadLoadPreview"),
    costPreview: $("costPreview"),
    budgetPreview: $("budgetPreview"),
    designAdvice: $("designAdvice"),
    suggestBtn: $("suggestBtn"),
    testBtn: $("testBtn"),
    simStatus: $("simStatus"),
    sceneLoadCase: $("sceneLoadCase"),
    arena: $("arena"),
    deckPath: $("deckPath"),
    roadPath: $("roadPath"),
    girderPath: $("girderPath"),
    girderLines: $("girderLines"),
    crackGroup: $("crackGroup"),
    truck: $("truck"),
    loadArrow: $("loadArrow"),
    loadArrowText: $("loadArrowText"),
    spanDiagramText: $("spanDiagramText"),
    testTimeline: $("testTimeline"),
    overallResult: $("overallResult"),
    strengthCard: $("strengthCard"),
    deflectionCard: $("deflectionCard"),
    costCard: $("costCard"),
    stressValue: $("stressValue"),
    stressLimit: $("stressLimit"),
    strengthState: $("strengthState"),
    strengthBar: $("strengthBar"),
    strengthNote: $("strengthNote"),
    deflectionValue: $("deflectionValue"),
    deflectionLimit: $("deflectionLimit"),
    deflectionState: $("deflectionState"),
    deflectionBar: $("deflectionBar"),
    deflectionNote: $("deflectionNote"),
    costValue: $("costValue"),
    costLimit: $("costLimit"),
    costState: $("costState"),
    costBar: $("costBar"),
    costNote: $("costNote"),
    inspectorTitle: $("inspectorTitle"),
    inspectorMessage: $("inspectorMessage"),
    deadLoadResult: $("deadLoadResult"),
    liveLoadResult: $("liveLoadResult"),
    momentResult: $("momentResult"),
    utilizationResult: $("utilizationResult"),
    campaignTrack: $("campaignTrack"),
    grade: $("gradeValue"),
    resetCampaignBtn: $("resetCampaignBtn"),
    soundBtn: $("soundBtn"),
    helpBtn: $("helpBtn"),
    helpDialog: $("helpDialog"),
    closeHelpBtn: $("closeHelpBtn"),
    resultDialog: $("resultDialog"),
    dialogIcon: $("dialogIcon"),
    dialogKicker: $("dialogKicker"),
    dialogTitle: $("dialogTitle"),
    dialogMessage: $("dialogMessage"),
    scoreBreakdown: $("scoreBreakdown"),
    closeResultBtn: $("closeResultBtn"),
    nextMissionBtn: $("nextMissionBtn"),
    tooltip: $("tooltip")
  };

  let state = loadState();
  let testing = false;
  let dialogAction = "next";
  let audioContext = null;

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem("buildsafe-v3"));
      if (!saved) return clone(DEFAULT_STATE);
      return {
        ...clone(DEFAULT_STATE),
        ...saved,
        bestScores: Array.isArray(saved.bestScores)
          ? saved.bestScores.concat([0, 0, 0, 0, 0, 0]).slice(0, 6)
          : [...DEFAULT_STATE.bestScores],
        completed: Array.isArray(saved.completed)
          ? saved.completed.concat([false, false, false, false, false, false]).slice(0, 6)
          : [...DEFAULT_STATE.completed]
      };
    } catch {
      return clone(DEFAULT_STATE);
    }
  }

  function saveState() {
    try {
      localStorage.setItem("buildsafe-v3", JSON.stringify(state));
    } catch {}
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function peso(value) {
    return "₱" + Math.round(value).toLocaleString("en-PH");
  }

  function mission() {
    return MISSIONS[state.missionIndex];
  }

  function selectedMaterialKey() {
    const checked = document.querySelector('input[name="material"]:checked');
    return checked ? checked.value : "steel";
  }

  function getDesign() {
    const materialKey = selectedMaterialKey();
    return {
      materialKey,
      material: MATERIALS[materialKey],
      width: Number(els.width.value),
      depth: Number(els.depth.value),
      girders: Number(els.girders.value)
    };
  }

  function calculate() {
    const m = mission();
    const d = getDesign();

    const deckWidthM = 7.2;
    const deckThicknessM = 0.20;
    const concreteUnitWeight = 24;
    const impactFactor = 1.15;

    const grossAreaMm2 = d.width * d.depth;
    const effectiveAreaM2 = grossAreaMm2 * d.material.areaFactor / 1e6;
    const effectiveI = d.width * Math.pow(d.depth, 3) / 12 * d.material.inertiaFactor;

    const girderSelfWeightKnM =
      effectiveAreaM2 * d.material.density * 9.81 / 1000;

    const deckDeadLoadTotalKnM =
      deckWidthM * deckThicknessM * concreteUnitWeight;

    const deadLoadPerGirderKnM =
      deckDeadLoadTotalKnM / d.girders + girderSelfWeightKnM;

    const dynamicVehicleTotalKn = m.load * impactFactor;
    const vehiclePerGirderKn = dynamicVehicleTotalKn / d.girders;

    const factoredMomentKnM =
      1.2 * deadLoadPerGirderKnM * Math.pow(m.span, 2) / 8 +
      1.6 * vehiclePerGirderKn * m.span / 4;

    const stressMpa =
      factoredMomentKnM * 1e6 * (d.depth / 2) / effectiveI;

    const spanMm = m.span * 1000;
    const deadDeflectionMm =
      5 * deadLoadPerGirderKnM * Math.pow(spanMm, 4) /
      (384 * d.material.E * effectiveI);

    const liveDeflectionMm =
      vehiclePerGirderKn * 1000 * Math.pow(spanMm, 3) /
      (48 * d.material.E * effectiveI);

    const deflectionMm = deadDeflectionMm + liveDeflectionMm;
    const deflectionLimitMm = spanMm / 800;

    const girderVolumeM3 = effectiveAreaM2 * m.span * d.girders;
    const girderMassKg = girderVolumeM3 * d.material.density;
    const deckVolumeM3 = deckWidthM * deckThicknessM * m.span;
    const deckMassKg = deckVolumeM3 * 2400;

    const girderCost = d.material.costPerKg
      ? girderMassKg * d.material.costPerKg
      : girderVolumeM3 * d.material.costPerM3;

    const deckCost = deckVolumeM3 * 12000;
    const substructureAllowance = 320000 + m.span * 18000;
    const connectionAllowance = d.girders * 25000;
    const totalCost =
      girderCost + deckCost + substructureAllowance + connectionAllowance;

    const strengthRatio = stressMpa / d.material.stressLimit;
    const deflectionRatio = deflectionMm / deflectionLimitMm;
    const budgetRatio = totalCost / m.budget;
    const governingRatio = Math.max(strengthRatio, deflectionRatio);

    return {
      ...d,
      deckWidthM,
      deckThicknessM,
      impactFactor,
      effectiveAreaM2,
      effectiveI,
      girderSelfWeightKnM,
      deckDeadLoadTotalKnM,
      deadLoadPerGirderKnM,
      dynamicVehicleTotalKn,
      vehiclePerGirderKn,
      factoredMomentKnM,
      stressMpa,
      deadDeflectionMm,
      liveDeflectionMm,
      deflectionMm,
      deflectionLimitMm,
      girderMassKg,
      deckMassKg,
      totalMassKg: girderMassKg + deckMassKg,
      totalCost,
      strengthRatio,
      deflectionRatio,
      budgetRatio,
      governingRatio,
      pass:
        strengthRatio <= 1 &&
        deflectionRatio <= 1 &&
        budgetRatio <= 1
    };
  }

  function renderMission() {
    const m = mission();
    els.missionNumber.textContent =
      "MISSION " + String(state.missionIndex + 1).padStart(2, "0");
    els.difficulty.textContent = m.difficulty;
    els.missionTitle.textContent = m.title;
    els.missionStory.textContent = m.story;
    els.missionSpan.textContent = m.span.toFixed(1) + " m";
    els.missionLoad.textContent = m.load.toLocaleString() + " kN";
    els.missionBudget.textContent = peso(m.budget);
    els.attempts.textContent = state.attempts;
    els.loadArrowText.textContent = m.load.toLocaleString() + " kN vehicle";
    els.spanDiagramText.textContent = m.span.toFixed(1) + " m CLEAR SPAN";
    renderCampaign();
    renderPlayer();
    resetInspection();
    updatePreview();
  }

  function renderPlayer() {
    const level = Math.floor(state.xp / 500) + 1;
    const within = state.xp % 500;
    els.level.textContent = level;
    els.xp.textContent = within + " / 500";
    els.xpBar.style.width = within / 5 + "%";
    els.score.textContent = state.score.toLocaleString();

    const done = state.completed.filter(Boolean).length;
    let grade = "C · Junior Designer";
    if (done >= 2 || state.score >= 1000) grade = "B · Project Engineer";
    if (done >= 4 || state.score >= 2400) grade = "A · Senior Engineer";
    if (done === 6 && state.score >= 4000) grade = "S · Chief Bridge Engineer";
    els.grade.textContent = grade;
  }

  function renderCampaign() {
    els.campaignTrack.innerHTML = "";
    MISSIONS.forEach((item, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className =
        "mission-node" +
        (state.completed[index] ? " complete" : "") +
        (index === state.missionIndex ? " active" : "") +
        (index > state.unlocked ? " locked" : "");
      button.disabled = index > state.unlocked;
      button.innerHTML =
        "<span>PROJECT " + String(index + 1).padStart(2, "0") + "</span>" +
        "<strong>" + item.title + "</strong>" +
        "<em>" +
        (state.completed[index]
          ? "✓ " + (state.bestScores[index] || 0).toLocaleString() + " pts"
          : index > state.unlocked
            ? "LOCKED"
            : "AVAILABLE") +
        "</em>";

      button.addEventListener("click", () => {
        if (testing || index > state.unlocked) return;
        state.missionIndex = index;
        state.attempts = 3;
        saveState();
        applySuggestedDesign(false);
        renderMission();
      });

      els.campaignTrack.appendChild(button);
    });
  }

  function updatePreview() {
    const r = calculate();
    els.widthOut.textContent = r.width + " mm";
    els.depthOut.textContent = r.depth + " mm";
    els.girderOut.textContent = r.girders + " girders";
    els.widthDiagram.textContent = r.width;
    els.depthDiagram.textContent = r.depth;
    els.girderMassPreview.textContent =
      (r.girderMassKg / 1000).toFixed(1) + " t";
    els.deadLoadPreview.textContent =
      r.deadLoadPerGirderKnM.toFixed(1) + " kN/m each";
    els.costPreview.textContent = peso(r.totalCost);
    els.budgetPreview.textContent =
      Math.round(r.budgetRatio * 100) + "%";

    els.budgetPreview.style.color =
      r.budgetRatio > 1
        ? "var(--red)"
        : r.budgetRatio > 0.92
          ? "var(--yellow)"
          : "";

    updateSectionShape(r.materialKey);
    updateGirderLines(r.girders);
    updateAdvice(r);
    clearPresetHighlight();
  }

  function updateSectionShape(materialKey) {
    els.sectionShape.classList.remove("timber-shape", "aluminum-shape");
    if (materialKey === "timber") {
      els.sectionShape.classList.add("timber-shape");
    } else if (materialKey === "aluminum") {
      els.sectionShape.classList.add("aluminum-shape");
    }
  }

  function updateGirderLines(count) {
    els.girderLines.innerHTML = "";
    const spacing = 8;
    const total = (count - 1) * spacing;
    for (let i = 0; i < count; i += 1) {
      const offset = i * spacing - total / 2;
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute(
        "d",
        "M156 " + (316 + offset) + " Q500 " + (316 + offset) + " 844 " + (316 + offset)
      );
      els.girderLines.appendChild(path);
    }
  }

  function updateAdvice(r) {
    let title = "Design tip";
    let message =
      "Run the load test to see the actual strength and deflection checks.";

    if (r.budgetRatio > 1) {
      title = "Budget warning";
      message =
        "Your current concept is over budget. Reduce girder size/count or choose a more economical material.";
    } else if (r.materialKey === "timber" && mission().span >= 14) {
      title = "Stiffness warning";
      message =
        "Timber can work in the game, but longer spans usually need deeper sections because deflection may govern.";
    } else if (r.materialKey === "aluminum") {
      title = "Cost warning";
      message =
        "Aluminum reduces self-weight, but its high material cost can quickly consume the project budget.";
    } else {
      message =
        "Balanced designs usually perform better than simply making every member as large as possible.";
    }

    els.designAdvice.querySelector("strong").textContent = title;
    els.designAdvice.querySelector("p").textContent = message;
  }

  function clearPresetHighlight() {
    document.querySelectorAll("[data-preset]").forEach((btn) => {
      btn.classList.remove("selected");
    });
  }

  function applyPreset(name) {
    const p = PRESETS[name];
    if (!p) return;
    els.width.value = p.width;
    els.depth.value = p.depth;
    els.girders.value = p.girders;
    document.querySelectorAll("[data-preset]").forEach((btn) => {
      btn.classList.toggle("selected", btn.dataset.preset === name);
    });
    updatePreview();
    document.querySelector('[data-preset="' + name + '"]').classList.add("selected");
  }

  function applySuggestedDesign(announce = true) {
    const s = mission().suggested;
    const radio = document.querySelector(
      'input[name="material"][value="' + s.material + '"]'
    );
    if (radio) radio.checked = true;
    els.width.value = s.width;
    els.depth.value = s.depth;
    els.girders.value = s.girders;
    updatePreview();
    if (announce) {
      els.designAdvice.querySelector("strong").textContent =
        "Suggested starting design loaded";
      els.designAdvice.querySelector("p").textContent =
        "This setup is intentionally conservative. Pass the test first, then optimize it for a higher score.";
      tone(520, 0.06);
    }
  }

  function resetInspection() {
    setStatus("Ready to test", "");
    els.sceneLoadCase.textContent = "Service condition";
    els.crackGroup.hidden = true;
    setBridgeSag(0, false);
    els.truck.setAttribute("transform", "translate(83 220)");
    els.loadArrow.classList.remove("active");

    els.overallResult.textContent = "Not tested";
    els.overallResult.className = "overall-result neutral";

    [
      [els.strengthCard, els.strengthState, els.strengthBar],
      [els.deflectionCard, els.deflectionState, els.deflectionBar],
      [els.costCard, els.costState, els.costBar]
    ].forEach(([card, stateEl, bar]) => {
      card.className = "check-card";
      stateEl.textContent = "Waiting";
      bar.style.width = "0%";
      bar.style.background = "var(--blue)";
    });

    els.stressValue.textContent = "—";
    els.stressLimit.textContent = "—";
    els.deflectionValue.textContent = "—";
    els.deflectionLimit.textContent = "—";
    els.costValue.textContent = "—";
    els.costLimit.textContent = peso(mission().budget);

    els.strengthNote.textContent =
      "Run the load test to calculate factored bending demand.";
    els.deflectionNote.textContent =
      "Game service limit uses L/800.";
    els.costNote.textContent =
      "Includes deck, girders and simplified substructure allowance.";

    els.deadLoadResult.textContent = "—";
    els.liveLoadResult.textContent = "—";
    els.momentResult.textContent = "—";
    els.utilizationResult.textContent = "—";

    els.inspectorTitle.textContent = "Ready for your design";
    els.inspectorMessage.textContent =
      "Use the controls on the left, then run the load test. I’ll explain exactly what passed or failed.";

    setTimeline("");
  }

  function setTimeline(stage) {
    const order = ["dead", "vehicle", "inspect"];
    const index = order.indexOf(stage);
    els.testTimeline.querySelectorAll("[data-stage]").forEach((node) => {
      const nodeIndex = order.indexOf(node.dataset.stage);
      node.classList.remove("active", "done");
      if (nodeIndex < index) node.classList.add("done");
      if (node.dataset.stage === stage) node.classList.add("active");
      if (stage === "complete") node.classList.add("done");
    });
  }

  function setStatus(text, type) {
    els.simStatus.classList.remove("testing", "pass", "fail");
    if (type) els.simStatus.classList.add(type);
    els.simStatus.querySelector("span").textContent = text;
  }

  function setBridgeSag(ratio, failed) {
    const visibleSag = clamp(ratio, 0, 1.35) * 22;
    const deckMid = 282 + visibleSag;
    const roadMid = 275 + visibleSag;
    const girderMid = 304 + visibleSag;

    els.deckPath.setAttribute(
      "d",
      "M145 282 Q500 " + deckMid.toFixed(1) + " 855 282"
    );
    els.roadPath.setAttribute(
      "d",
      "M145 275 Q500 " + roadMid.toFixed(1) + " 855 275"
    );
    els.girderPath.setAttribute(
      "d",
      "M156 304 Q500 " + girderMid.toFixed(1) + " 844 304"
    );

    els.girderPath.style.stroke = failed
      ? "#b44249"
      : ratio > 0.9
        ? "#9b7f40"
        : "#53616a";
  }

  function ratioClass(ratio) {
    if (ratio > 1) return "fail";
    if (ratio > 0.9) return "warn";
    return "pass";
  }

  function updateCheck(card, stateEl, bar, ratio, passLabel = "PASS") {
    const cls = ratioClass(ratio);
    card.className = "check-card " + cls;
    stateEl.textContent =
      cls === "fail" ? "FAIL" : cls === "warn" ? "NEAR LIMIT" : passLabel;
    bar.style.width = clamp(ratio * 100, 0, 100) + "%";
    bar.style.background =
      cls === "fail"
        ? "var(--red)"
        : cls === "warn"
          ? "var(--yellow)"
          : "var(--green)";
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function tone(freq = 440, duration = 0.08, gainValue = 0.04) {
    if (!state.sound) return;
    try {
      audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(gainValue, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(
        0.0001,
        audioContext.currentTime + duration
      );
      osc.connect(gain);
      gain.connect(audioContext.destination);
      osc.start();
      osc.stop(audioContext.currentTime + duration);
    } catch {}
  }

  async function animateTruck(result, duration) {
    const start = performance.now();

    await new Promise((resolve) => {
      function frame(now) {
        const p = clamp((now - start) / duration, 0, 1);
        const x = 83 + p * 730;
        els.truck.setAttribute(
          "transform",
          "translate(" + x.toFixed(1) + " 220)"
        );

        const positionEffect = Math.sin(Math.PI * p);
        const totalRatio =
          result.deflectionRatio * 0.25 +
          result.governingRatio * 0.75;
        setBridgeSag(totalRatio * positionEffect, false);

        if (p > 0.42 && p < 0.58) {
          els.loadArrow.classList.add("active");
        } else {
          els.loadArrow.classList.remove("active");
        }

        if (p < 1) requestAnimationFrame(frame);
        else resolve();
      }
      requestAnimationFrame(frame);
    });
  }

  async function runLoadTest() {
    if (testing) return;
    testing = true;
    document.body.classList.add("testing");
    els.testBtn.disabled = true;
    resetInspection();

    const result = calculate();
    const reduced =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    setStatus("Applying dead load", "testing");
    els.sceneLoadCase.textContent = "Stage 1 · Dead load";
    setTimeline("dead");
    tone(310, 0.06);
    setBridgeSag(result.deflectionRatio * 0.25, false);
    await sleep(reduced ? 200 : 850);

    setStatus("Vehicle crossing", "testing");
    els.sceneLoadCase.textContent = "Stage 2 · Dynamic vehicle load";
    setTimeline("vehicle");
    tone(380, 0.06);
    await animateTruck(result, reduced ? 450 : 2800);

    setStatus("Engineering inspection", "testing");
    els.sceneLoadCase.textContent = "Stage 3 · Inspection";
    setTimeline("inspect");
    els.loadArrow.classList.remove("active");
    await sleep(reduced ? 180 : 700);

    finalizeTest(result);

    testing = false;
    document.body.classList.remove("testing");
    els.testBtn.disabled = false;
  }

  function finalizeTest(r) {
    setTimeline("complete");

    els.stressValue.textContent = r.stressMpa.toFixed(1) + " MPa";
    els.stressLimit.textContent = r.material.stressLimit.toFixed(0) + " MPa";
    els.deflectionValue.textContent = r.deflectionMm.toFixed(1) + " mm";
    els.deflectionLimit.textContent = r.deflectionLimitMm.toFixed(1) + " mm";
    els.costValue.textContent = peso(r.totalCost);
    els.costLimit.textContent = peso(mission().budget);

    updateCheck(
      els.strengthCard,
      els.strengthState,
      els.strengthBar,
      r.strengthRatio
    );
    updateCheck(
      els.deflectionCard,
      els.deflectionState,
      els.deflectionBar,
      r.deflectionRatio
    );
    updateCheck(
      els.costCard,
      els.costState,
      els.costBar,
      r.budgetRatio
    );

    els.strengthNote.textContent =
      Math.round(r.strengthRatio * 100) +
      "% of the simplified design stress limit.";
    els.deflectionNote.textContent =
      Math.round(r.deflectionRatio * 100) +
      "% of the game L/800 service limit.";
    els.costNote.textContent =
      Math.round(r.budgetRatio * 100) +
      "% of the available project budget.";

    els.deadLoadResult.textContent =
      r.deadLoadPerGirderKnM.toFixed(1) + " kN/m";
    els.liveLoadResult.textContent =
      r.vehiclePerGirderKn.toFixed(1) + " kN";
    els.momentResult.textContent =
      r.factoredMomentKnM.toFixed(0) + " kN·m";
    els.utilizationResult.textContent =
      Math.round(r.governingRatio * 100) + "%";

    if (r.pass) {
      handlePass(r);
    } else {
      handleFail(r);
    }
  }

  function handlePass(r) {
    setStatus("Bridge approved", "pass");
    els.sceneLoadCase.textContent = "Inspection complete · PASS";
    els.overallResult.textContent = "Approved";
    els.overallResult.className = "overall-result pass";
    setBridgeSag(r.deflectionRatio, false);

    let inspector =
      "All three checks passed. The bridge is strong enough, serviceable, and within the mission budget.";

    if (r.governingRatio < 0.55 && r.budgetRatio > 0.9) {
      inspector =
        "Safe, but conservative. You can probably reduce material and improve the project score.";
    } else if (r.governingRatio >= 0.75 && r.governingRatio <= 0.92) {
      inspector =
        "Very efficient structural use. You are close to the target zone without exceeding the limit.";
    }

    els.inspectorTitle.textContent = "Design accepted";
    els.inspectorMessage.textContent = inspector;

    const structureEfficiency = Math.round(
      clamp(100 - Math.abs(r.governingRatio - 0.82) * 145, 35, 100)
    );
    const budgetEfficiency = Math.round(
      clamp(115 - r.budgetRatio * 70, 25, 100)
    );
    const attemptBonus = state.attempts * 30;
    const missionScore = Math.round(
      180 +
      structureEfficiency * 2.1 +
      budgetEfficiency * 1.7 +
      attemptBonus
    );
    const xpGain = Math.round(110 + missionScore * 0.22);

    state.score += missionScore;
    state.xp += xpGain;
    state.bestScores[state.missionIndex] = Math.max(
      state.bestScores[state.missionIndex],
      missionScore
    );
    state.completed[state.missionIndex] = true;

    if (state.missionIndex < MISSIONS.length - 1) {
      state.unlocked = Math.max(state.unlocked, state.missionIndex + 1);
    }

    saveState();
    renderPlayer();
    renderCampaign();

    tone(660, 0.11);
    setTimeout(() => tone(880, 0.12), 110);

    showResult({
      pass: true,
      title:
        state.missionIndex === MISSIONS.length - 1
          ? "Final project approved"
          : "Bridge approved",
      message:
        "Your bridge passed strength, serviceability, and budget checks. Good engineering balances safety with efficient use of material.",
      items: [
        ["Project score", missionScore.toLocaleString()],
        ["XP earned", "+" + xpGain],
        ["Structural use", Math.round(r.governingRatio * 100) + "%"]
      ]
    });
  }

  function handleFail(r) {
    state.attempts = Math.max(0, state.attempts - 1);
    saveState();
    els.attempts.textContent = state.attempts;

    setStatus("Design needs revision", "fail");
    els.sceneLoadCase.textContent = "Inspection complete · FAIL";
    els.overallResult.textContent = "Revise design";
    els.overallResult.className = "overall-result fail";
    els.crackGroup.hidden = r.strengthRatio <= 1 && r.deflectionRatio <= 1;
    setBridgeSag(r.governingRatio, true);
    els.arena.classList.add("fail-shake");
    setTimeout(() => els.arena.classList.remove("fail-shake"), 750);

    const reasons = failureReasons(r);
    els.inspectorTitle.textContent = "Design not accepted";
    els.inspectorMessage.textContent = reasons.guidance;
    tone(145, 0.18, 0.055);

    showResult({
      pass: false,
      exhausted: state.attempts === 0,
      title:
        state.attempts === 0
          ? "Project test limit reached"
          : "Bridge needs revision",
      message:
        reasons.summary +
        (state.attempts > 0
          ? " You have " + state.attempts + " test attempt" + (state.attempts === 1 ? "" : "s") + " left."
          : " Restart this project to try a new design."),
      items: [
        ["Strength", Math.round(r.strengthRatio * 100) + "%"],
        ["Deflection", Math.round(r.deflectionRatio * 100) + "%"],
        ["Budget", Math.round(r.budgetRatio * 100) + "%"]
      ]
    });
  }

  function failureReasons(r) {
    const failed = [];
    if (r.strengthRatio > 1) failed.push("strength");
    if (r.deflectionRatio > 1) failed.push("deflection");
    if (r.budgetRatio > 1) failed.push("budget");

    let guidance = "Revise the design before testing again.";

    if (failed.includes("strength") && failed.includes("deflection")) {
      guidance =
        "The bridge is both overstressed and too flexible. Increase girder depth, add girders, or select a stiffer material.";
    } else if (failed.includes("strength")) {
      guidance =
        "Bending stress is too high. Increase section size or distribute the vehicle load across more girders.";
    } else if (failed.includes("deflection")) {
      guidance =
        "The bridge moves too much under service load. Increasing girder depth is usually the most effective fix.";
    } else if (failed.includes("budget")) {
      guidance =
        "The structure is over budget. Reduce unnecessary material or choose a lower-cost system while keeping the safety checks green.";
    }

    return {
      summary:
        failed.length === 1
          ? "The " + failed[0] + " check failed."
          : "The " + failed.join(", ") + " checks failed.",
      guidance
    };
  }

  function showResult({ pass, exhausted = false, title, message, items }) {
    els.dialogIcon.textContent = pass ? "✓" : "!";
    els.dialogIcon.style.color = pass ? "var(--green)" : "var(--red)";
    els.dialogIcon.style.background = pass
      ? "rgba(79,209,138,.1)"
      : "rgba(240,100,111,.1)";
    els.dialogIcon.style.borderColor = pass
      ? "rgba(79,209,138,.3)"
      : "rgba(240,100,111,.3)";
    els.dialogKicker.textContent = pass
      ? "INSPECTION COMPLETE"
      : exhausted
        ? "TEST ATTEMPTS USED"
        : "REVISION REQUIRED";
    els.dialogTitle.textContent = title;
    els.dialogMessage.textContent = message;
    els.scoreBreakdown.innerHTML = items
      .map(
        ([label, value]) =>
          "<div><span>" +
          label +
          "</span><strong>" +
          value +
          "</strong></div>"
      )
      .join("");

    if (pass) {
      dialogAction = "next";
      els.nextMissionBtn.hidden = false;
      els.nextMissionBtn.textContent =
        state.missionIndex < MISSIONS.length - 1
          ? "Next project →"
          : "Replay final project";
    } else if (exhausted) {
      dialogAction = "restart";
      els.nextMissionBtn.hidden = false;
      els.nextMissionBtn.textContent = "Restart project";
    } else {
      dialogAction = "review";
      els.nextMissionBtn.hidden = true;
    }

    if (typeof els.resultDialog.showModal === "function") {
      els.resultDialog.showModal();
    } else {
      els.resultDialog.setAttribute("open", "");
    }
  }

  function closeDialog(dialog) {
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
  }

  function advanceFromDialog() {
    if (dialogAction === "restart") {
      state.attempts = 3;
      saveState();
      closeDialog(els.resultDialog);
      applySuggestedDesign(false);
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
      applySuggestedDesign(false);
      renderMission();
    }
  }

  function resetCampaign() {
    const ok = window.confirm(
      "Reset all BuildSafe campaign progress, scores, and XP?"
    );
    if (!ok) return;

    state = clone(DEFAULT_STATE);
    saveState();
    applySuggestedDesign(false);
    renderMission();
  }

  function showTooltip(button) {
    const message = button.dataset.tip;
    if (!message) return;
    els.tooltip.textContent = message;
    els.tooltip.classList.add("show");
    const rect = button.getBoundingClientRect();
    const left = clamp(
      rect.left + rect.width / 2 - 110,
      8,
      window.innerWidth - 248
    );
    const top = rect.bottom + 7;
    els.tooltip.style.left = left + "px";
    els.tooltip.style.top = top + "px";
  }

  function hideTooltip() {
    els.tooltip.classList.remove("show");
  }

  [els.width, els.depth, els.girders].forEach((input) => {
    input.addEventListener("input", updatePreview);
  });

  document.querySelectorAll('input[name="material"]').forEach((input) => {
    input.addEventListener("change", updatePreview);
  });

  document.querySelectorAll("[data-preset]").forEach((button) => {
    button.addEventListener("click", () => applyPreset(button.dataset.preset));
  });

  document.querySelectorAll(".info-dot").forEach((button) => {
    button.addEventListener("mouseenter", () => showTooltip(button));
    button.addEventListener("mouseleave", hideTooltip);
    button.addEventListener("focus", () => showTooltip(button));
    button.addEventListener("blur", hideTooltip);
    button.addEventListener("click", () => {
      if (els.tooltip.classList.contains("show")) hideTooltip();
      else showTooltip(button);
    });
  });

  els.suggestBtn.addEventListener("click", () => applySuggestedDesign(true));
  els.testBtn.addEventListener("click", runLoadTest);
  els.closeResultBtn.addEventListener("click", () =>
    closeDialog(els.resultDialog)
  );
  els.nextMissionBtn.addEventListener("click", advanceFromDialog);
  els.resetCampaignBtn.addEventListener("click", resetCampaign);

  els.helpBtn.addEventListener("click", () => {
    if (typeof els.helpDialog.showModal === "function") {
      els.helpDialog.showModal();
    } else {
      els.helpDialog.setAttribute("open", "");
    }
  });

  els.closeHelpBtn.addEventListener("click", () =>
    closeDialog(els.helpDialog)
  );

  els.soundBtn.addEventListener("click", () => {
    state.sound = !state.sound;
    els.soundBtn.textContent = state.sound ? "🔊" : "🔇";
    els.soundBtn.setAttribute(
      "aria-label",
      state.sound ? "Mute sound" : "Enable sound"
    );
    saveState();
    if (state.sound) tone(520, 0.06);
  });

  [els.resultDialog, els.helpDialog].forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closeDialog(dialog);
    });
  });

  window.addEventListener("resize", hideTooltip);

  els.soundBtn.textContent = state.sound ? "🔊" : "🔇";
  applySuggestedDesign(false);
  renderMission();
})();