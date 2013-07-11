## Script (Python) "guard_unassign_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


if context.portal_type != 'AnalysisRequest':
    # Check analysis permission against parent
    mtool = context.portal_membership
    if mtool.checkPermission("BIKA: Unassign analyses", context.aq_parent):
        return True
    return False

if context.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
    return True

if not context.getAnalyses(worksheetanalysis_review_state = 'assigned'):
    return True

return False
